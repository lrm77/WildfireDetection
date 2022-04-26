/*
 * Software used to display a stream from a thermal camera and 
 * capture images.
 * Used for experiments to characterize thermal images by distance 
 * and temperature.
 *
 * Wildfire Detection Project
 * ECE 6960 - Computational Photography
 * Luke Majors, Ian Lavin, Colin Pollard
 */

#include <stdio.h>
#include <signal.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>
#include <string.h>
#include <math.h>

#include <seekware/seekware.h>

#ifdef __linux__
#include <sys/utsname.h>
#include <SDL2/SDL.h>
#include <SDL2/SDL_ttf.h>
#endif

#include "../include/ThermalCamera.hpp"

// Scale used for displaying stream from camera
#define SCALE_FACTOR 4

// Number of cameras physically connected to USB input
#define CAMS_CONNECTED 3

/* Defines how the preview is displayed */
typedef enum display_mode_t
{
  DISPLAY_ARGB = 0,
  DISPLAY_THERMAL = 1,
} display_mode_t;

bool exit_requested = false;

// Default the display mode to thermal
display_mode_t display_mode = DISPLAY_THERMAL;

static void signal_callback(int signum)
{
  printf("\nExit requested!\n");
  exit_requested = true;
}

/* Displays a help message for program usage */
static void help(const char *name)
{
  printf(
      "Usage: %s [option]...\n"
      "Valid options are:\n"
      "   -h | --help                             Prints help.\n"
      "   -display-thermal | --display-thermal    Demonstrates how to draw a grayscale image using fixed point U16 thermography data from the camera\n"
      "                         ",
      name);
}

/* Parse command line arguments */
static int parse_cmdline(int argc, char **argv)
{
  for (int i = 1; i < argc; ++i)
  {
    if (!strcmp(argv[i], "-h") || !strcmp(argv[i], "--help"))
    {
      help(argv[0]);
      return 0;
    }

    else if (!strcmp(argv[i], "-display-argb") || !strcmp(argv[i], "---display-argb"))
    {
      display_mode = DISPLAY_ARGB;
    }
    else
    {
      fprintf(stderr, "Unknown parameter: \"%s\"\n", argv[i]);
      help(argv[0]);
      return 1;
    }
  }
  return 1;
}

//Perform a simple min/max linear stretch to transform U16 grayscale image data to ARGB8888
//For advanced AGC options that are highly customizable, please see the AGC settings listed in the Seekware User Guide.
void simple_agc(uint16_t *u16_input, size_t elements_in, uint32_t *argb_output, size_t elements_out)
{
  if (u16_input == NULL || argb_output == NULL)
  {
    return;
  }

  size_t i = 0;
  uint16_t min = 7000;
  uint16_t max = 0;
  uint16_t pixel_in = 0;

  //Find min and max of the input
  for (i = 0; i < elements_in; ++i)
  {
    pixel_in = u16_input[i];
    if (pixel_in > max)
    {
      max = pixel_in;
    }
    if (pixel_in < min)
    {
      min = pixel_in;
    }
  }

  //Find relative intensity based on min/max. Assign output RGB channels to computed 8bit luminance.
  uint16_t delta = max - min;
  uint32_t luminance = 0;
  float relative_intensity = 0.0f;
  if (delta > 0)
  {
    for (i = 0; i < elements_out; ++i)
    {
      relative_intensity = (float)(u16_input[i] - min) / delta;
      luminance = (uint32_t)(relative_intensity * 255.0f);
      argb_output[i] = 0xFF000000 | luminance << 16 | luminance << 8 | luminance;
    }
  }
}

int main(int argc, char **argv)
{
  int offset = 3; // Pixel offset for drawing target

  /* Data for displaying camera stream */
  int window_texture_pitch = 0;
  size_t frame_count = 0;
  size_t frame_pixels = 0;
  uint16_t *thermography_data = NULL;
  uint32_t *window_texture_data = NULL;

  /* Variables to keep track of connected cameras */
  bool camera_running = false;
  psw camera = NULL;
  sw_retcode status = SW_RETCODE_NONE;
  std::vector<std::unique_ptr<ThermalCamera>> cams;
  int cam_index = 0;

  /* Variables for handling display GUI */
  SDL_Event event;
  SDL_Window *window = NULL;
  SDL_Renderer *window_renderer = NULL;
  SDL_Texture *window_texture = NULL;

  // Position of center pixel
  int center_x, center_y; 

  // Flag set true when a capture is requested
  bool capture = false;   

  // Path where captured images are written
  std::string savepath = "/home/pi/imageData/";

  // Used to construct the filename for each captured image
  std::string filename, temp_str, dist_str;

  // Register signal handlers for safely closing program
  signal(SIGINT, signal_callback);
  signal(SIGTERM, signal_callback);

  printf("Starting Display for Thermal Camera...\n");
  printf("Press <RETURN> to cycle through connected cameras\n");
  printf("Press <SPACE> to capture a series of images\n\n");

  /* * * * * * * * * * * * * Initialize Seek SDK * * * * * * * * * * * * * * */

  //Open the connected Seek Cameras 
  for(int i = 0; i < CAMS_CONNECTED; i++)
	  cams.push_back(std::make_unique<ThermalCamera>());
  camera = cams[0]->get_camera_ptr();
  if(camera == NULL)
    exit(0);
  frame_pixels = (size_t)camera->frame_cols * (size_t)camera->frame_rows;
  center_x = camera->frame_cols/2;
  center_y = camera->frame_rows/2;
  std::cout << "Target displayed at position: (" << center_x << ", " << center_y << ")" << std::endl;

  // Parse the command line to additional settings
  if (parse_cmdline(argc, argv) == 0)
  {
    goto cleanup;
  }

  // Allocate memory for capturing image
  thermography_data = (uint16_t *)malloc(frame_pixels * sizeof(uint16_t));


  /* * * * * * * * * * * * * Initialize SDL * * * * * * * * * * * * * * */

  if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS) == 0)
  {
    SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "1");
    printf("Display driver: %s\n", SDL_GetVideoDriver(0));
  }
  else
  {
    perror("Error: Cannot initialize SDL2");
    goto cleanup;
  }

  // Initialize an SDL window:
  window = SDL_CreateWindow(
      "seekware-sdl",                    // window title
      100,                               // initial x position
      100,                               // initial y position
      camera->frame_cols * SCALE_FACTOR, // width, in pixels
      camera->frame_rows * SCALE_FACTOR, // height, in pixels
      SDL_WINDOW_SHOWN                   // present window on creation
      );
  if (window == NULL)
  {
    fprintf(stdout, "Could not create SDL window: %s\n", SDL_GetError());
    goto cleanup;
  }

#if SDL_VERSION_ATLEAST(2, 0, 5)
  SDL_SetWindowResizable(window, SDL_TRUE);
#endif

  //Initialize an SDL Renderer
  struct utsname host_info;
  memset(&host_info, 0, sizeof(host_info));
  uname(&host_info);
  window_renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_SOFTWARE);

  if (window_renderer == NULL)
  {
    fprintf(stdout, "Could not create SDL window renderer: %s\n", SDL_GetError());
    goto cleanup;
  }

  if (SDL_RenderSetLogicalSize(window_renderer, camera->frame_cols, camera->frame_rows) < 0)
  {
    fprintf(stdout, "Could not set logical size of the SDL window renderer: %s\n", SDL_GetError());
    goto cleanup;
  }

  //Create a backing texture for the SDL window
  window_texture = SDL_CreateTexture(window_renderer, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STREAMING, camera->frame_cols, camera->frame_rows);
  if (window_texture == NULL)
  {
    fprintf(stdout, "Could not create SDL window texture: %s\n", SDL_GetError());
    goto cleanup;
  }

  /* * * * * * * * * * * * * Imaging Loop * * * * * * * * * * * * * * */

  do
  {
    //Lock the backing texture and get a pointer for accessing the texture memory directly
    if (SDL_LockTexture(window_texture, NULL, (void **)(&window_texture_data), &window_texture_pitch) != 0)
    {
      fprintf(stdout, "Could not lock SDL window texture: %s\n", SDL_GetError());
      exit_requested = true;
      continue;
    }

    //Get data from the camera
    if (display_mode == DISPLAY_ARGB)
    {
      // Pass a pointer to the texture directly into Seekware_GetImage for maximum performance
      status = Seekware_GetDisplayImage(camera, window_texture_data, (uint32_t)frame_pixels);
    }
    if (display_mode == DISPLAY_THERMAL)
    {
      status = Seekware_GetThermographyImage(camera, thermography_data, (uint32_t)frame_pixels);
    }

    //Check for errors
    if (camera_running)
    {
      if (status == SW_RETCODE_NOFRAME)
      {
        printf(" Seek Camera Timeout ...\n");
      }
      if (status == SW_RETCODE_DISCONNECTED)
      {
        printf(" Seek Camera Disconnected ...\n");
      }
      if (status != SW_RETCODE_NONE)
      {
        printf(" Seek Camera Error : %u ...\n", status);
        break;
      }
    }

    //Do AGC
    if (display_mode == DISPLAY_THERMAL)
    {
      simple_agc(thermography_data, frame_pixels, window_texture_data, frame_pixels);
    }

    //Unlock texture
    SDL_UnlockTexture(window_texture);

    //Increment frame count
    ++frame_count;

    //Load Texture
    if (SDL_RenderCopyEx(window_renderer, window_texture, NULL, NULL, 0, NULL, SDL_FLIP_NONE) < 0)
    {
      fprintf(stdout, "\n Could not copy window texture to window renderer: %s\n", SDL_GetError());
      break;
    }

    //Draw Target in center of frame for aiming camera
    SDL_SetRenderDrawBlendMode(window_renderer, SDL_BLENDMODE_BLEND);
    SDL_SetRenderDrawColor(window_renderer, 0x00, 0x00, 0x00, 0xFF);

    SDL_RenderDrawLine(window_renderer, center_x-1, center_y - offset, center_x-1, center_y + offset);
    SDL_RenderDrawLine(window_renderer, center_x - offset, center_y-1, center_x + offset, center_y-1);
    SDL_RenderDrawLine(window_renderer, center_x+1, center_y - offset, center_x+1, center_y + offset);
    SDL_RenderDrawLine(window_renderer, center_x - offset, center_y+1, center_x + offset, center_y+1);

    //Blit
    SDL_RenderPresent(window_renderer);

    //Check for SDL window events
    while (SDL_PollEvent(&event))
    {
      if (event.type == SDL_WINDOWEVENT && event.window.event == SDL_WINDOWEVENT_CLOSE)
      {
        exit_requested = true;
      }
      // Capture 10 images when space key is pressed
      if (event.type == SDL_KEYDOWN && event.key.keysym.scancode == SDL_SCANCODE_SPACE) {
	  std::cout << "Enter temperature: ";
	  std::cin >> temp_str;
	  std::cout << "Enter distance: ";
	  std::cin >> dist_str;
	  filename = savepath + "Testing_02-23-22_" + temp_str + "_" + dist_str + "_";
	  for(int i = 0; i < 10; i++) {
	    cams[cam_index]->capture_image(filename + std::to_string(i) + ".png");
	  }
      }
      // Cycle through connected cameras when return key is pressed
      if (event.type == SDL_KEYDOWN && event.key.keysym.scancode == SDL_SCANCODE_RETURN) {
	      cam_index++;
	      cam_index = cam_index % CAMS_CONNECTED;
	      camera = cams[cam_index]->get_camera_ptr();
      }
    }

  } while (!exit_requested);

  /* * * * * * * * * * * * * Cleanup * * * * * * * * * * * * * * */
cleanup:

  printf("Exiting...\n");

  if (camera != NULL)
  {
    Seekware_Close(camera);
  }
  if (thermography_data != NULL)
  {
    free(thermography_data);
  }
  if (window_texture != NULL)
  {
    SDL_DestroyTexture(window_texture);
  }
  if (window_renderer != NULL)
  {
    SDL_DestroyRenderer(window_renderer);
  }
  if (window != NULL)
  {
    SDL_DestroyWindow(window);
  }

  SDL_Quit();
  return 0;
}

/* * * * * * * * * * * * * End - of - File * * * * * * * * * * * * * * */
