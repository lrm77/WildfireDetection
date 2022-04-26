#include "../include/ThermalCamera.hpp"
#include <seekware/seekware.h>

#include <string>
#include <iostream>
#include <sstream>
#include <fstream>
#include <cstdio>
#include <cmath>
#include <cstdlib>
#include <opencv2/imgcodecs.hpp>
#include <unordered_map>

//Initialize Static Member Variables
int ThermalCamera::num_cams_found = 0;
bool ThermalCamera::initialized = false;
psw ThermalCamera::cam_list[NUM_CAMS] = {};
int ThermalCamera::next_camera_id = 0;
std::unordered_map<std::string, std::string> ThermalCamera::names;
std::string ThermalCamera::name_file = "/home/pi/TridentSensing/FireMapRS/Config/names.txt";

ThermalCamera::ThermalCamera()
{
    thermography_data = NULL;

    //Initialize cameras on first instantiation
    if (!initialized)
        ThermalCamera::init();

    // Select and open camera
    camera = get_camera();

    if (camera == NULL)
    {
        std::cout << error("Camera could not be connected.", "ThermalCamera") << std::endl;
	return;
    }

    serial_number = camera->serialNumber;

    name = names[serial_number];

    // Initialize camera settings
    initialize_camera(camera);

    frame_pixels = (size_t)camera->frame_cols * (size_t)camera->frame_rows;
    width = camera->frame_cols;
    height = camera->frame_rows;

    thermography_data = (uint16_t *)malloc(frame_pixels * sizeof(uint16_t));

    if (!thermography_data)
        std::cout << error("Failed to allocate memory for camera frame.", name) << std::endl;

    // Print camera information
    //std::cout << name << " ::Seek Camera Info::\n\n";
    //print_fw_info(camera);
}

ThermalCamera::~ThermalCamera()
{
    //Lock so only image can only be captured from one thread at a time
    //std::lock_guard<std::mutex> lock(m);

    std::cout << "Cleaning up Thermal Camera: " << name << "..." << std::endl;

    Seekware_Close(camera);

    if(thermography_data != NULL)
	free(thermography_data);
}

void ThermalCamera::capture_image(std::string filename)
{
    sw_retcode status;

    //Lock so only image can only be captured from one thread at a time
    std::lock_guard<std::mutex> lock(m);

    // Trigger Shutter
    int val = 1;
    Seekware_SetSettingEx(camera, SETTING_TRIGGER_SHUTTER, &val, 4);

    status = Seekware_GetThermographyImage(camera, thermography_data, (uint32_t)frame_pixels);

    if(status != SW_RETCODE_NONE) {
        std::cout << "Couldn't capture image. Error: " << status << "\n";
        std::cout << "Error from thing: " << SW_RETCODE_DISCONNECTED << std::endl;
        std::cout << error("Failed to capture image.", name) << std::endl;
    }

    cv::Mat mat(240, 320, CV_16UC1, thermography_data);
    
    bool result = imwrite(filename, mat);
    
    if (!result) {
        std::cout << "Failed to write image to file\n";
        std::cout << error("Failed to write image to file.", name) << std::endl;
    }

    // Write the data to a file
    //write_thermography_data_csv(camera, filename, thermography_data);
}

void ThermalCamera::init()
{
    std::cout << "Initializing Thermal Cameras...\n";
    sw_retcode status;

    status = Seekware_Find(cam_list, NUM_CAMS, &num_cams_found);
    if (status != SW_RETCODE_NONE || num_cams_found == 0)
    {
        std::cout << error("Cannot find any thermal cameras.", "ThermalCamera") << std::endl;
    }
    std::cout << "Thermal Cameras Initialized.\n"
              << "Cameras found: " << num_cams_found << "\n\n";

    ThermalCamera::initialize_names();

    initialized = true;
}

void ThermalCamera::print_fw_info(psw camera)
{
    sw_retcode status;
    int therm_ver;

    printf("Model Number:%s\n", camera->modelNumber);
    printf("SerialNumber: %s\n", camera->serialNumber);
    printf("Manufacture Date: %s\n", camera->manufactureDate);

    printf("Firmware Version: %u.%u.%u.%u\n",
           camera->fw_version_major,
           camera->fw_version_minor,
           camera->fw_build_major,
           camera->fw_build_minor);

    printf("Getting status\n");
    status = Seekware_GetSettingEx(camera, SETTING_THERMOGRAPHY_VERSION, &therm_ver, sizeof(therm_ver));
    printf("Status done\n");
    if (status != SW_RETCODE_NONE)
    {
        fprintf(stderr, "Error: Seek GetSetting returned %i\n", status);
    }
    printf("Themography Version: %i\n", therm_ver);

    sw_sdk_info sdk_info;
    Seekware_GetSdkInfo(NULL, &sdk_info);
    printf("Image Processing Version: %u.%u.%u.%u\n",
           sdk_info.lib_version_major,
           sdk_info.lib_version_minor,
           sdk_info.lib_build_major,
           sdk_info.lib_build_minor);

    printf("\n");
    fflush(stdout);
}

psw ThermalCamera::get_camera()
{
    sw_retcode status;
    psw cam = NULL;

    //Select the first camera that is not already open
    for (int i = 0; i < num_cams_found; ++i)
    {
        cam = cam_list[i];
        status = Seekware_Open(cam);
        if (status == SW_RETCODE_OPENEX)
        {
            cam = NULL;
            continue;
        }
        if (status != SW_RETCODE_NONE)
        {
            std::cout << "Could not open camera (" << status << ")\n";
        }
        break;
    }
    //Return the opened camera
    return cam;
}

void ThermalCamera::set_name(psw camera)
{
    if (names.find(camera->serialNumber) != names.end())
    {
        return;
    }

    std::string name = "";
    int id = 0;

    while (true)
    {
        std::ostringstream os;
        os << "ThermalCam" << ++id;
        name = os.str();

        bool name_exists = false;
        for (auto it = names.begin(); it != names.end(); ++it)
        {
            if (it->second.compare(name) == 0)
                name_exists = true;
        }
        if (!name_exists)
            break;
    }
    names[camera->serialNumber] = name;
}

void ThermalCamera::initialize_camera(psw camera)
{
    // Disable autoshutter
    int val = 0;
    Seekware_SetSettingEx(camera, SETTING_AUTOSHUTTER, &val, 4);

    // Set temperature units to Celcius
    Seekware_SetSetting(camera, SETTING_TEMP_UNITS, SW_TEMP_C);

    // Set to linear min/max AGC mode
    val = 1;
    Seekware_SetSettingEx(camera, SETTING_AGC_MODE, &val, 4);

    // Set to auto linear min/max
    val = 0;
    
    Seekware_SetSettingEx(camera, SETTING_LINMINMAX_MODE, &val, 4);

    // OR could set to manual mode
    // Seekware_SetSettingEx(camera, SETTING_LINMINMAX_MODE, &val, 4);
    // Set minimum and maximum values
    // int min = ...;
    // int max = ...;
    // Seekware_SetSettingEx(camera, SETTING_LINMINMAX_MIN_LOCK, &min, 4);
    // Seekware_SetSettingEx(camera, SETTING_LINMINMAX_MAX_LOCK, &max, 4);
}

int ThermalCamera::write_thermography_data_csv(psw camera, std::string filename, uint16_t *thermography_data)
{
    filename.append(".csv");
    FILE *log = fopen(filename.c_str(), "w");
    for (uint16_t i = 0; i < camera->frame_rows; ++i)
    {
        for (uint16_t j = 0; j < camera->frame_cols; ++j)
        {
            uint16_t value = thermography_data[(i * camera->frame_cols) + j];
            //uint16_t rounded_value = roundf(10.0f * value) / 10.0f;
            fprintf(log, "%d,", value);
        }
        fputc('\n', log);
    }
    fclose(log);
    return 0;
}

void ThermalCamera::read_names()
{
    std::ifstream f(name_file);

    // Do nothing if file doesn't exist
    if (!f.good())
        return;

    std::string serial;
    std::string name;
    while (f.good())
    {
        f >> serial;
        f >> name;
        names[serial] = name;
    }
    f.close();
}

void ThermalCamera::write_names()
{
    std::ofstream f(name_file); //, std::ofstream::trunc);

    // Check if file could be opened
    if (!f.good())
    {
        std::cout << "Could not write names file" << std::endl;
        return;
    }

    for (auto it = names.begin(); it != names.end(); ++it)
    {
        if (it->first == "")
            continue;
        f << it->first << " " << it->second << "\n";
    }

    f.close();
}

void ThermalCamera::initialize_names()
{
    read_names();

    for (int i = 0; i < num_cams_found; ++i)
    {
        set_name(cam_list[i]);
    }

    write_names();
}

size_t ThermalCamera::get_frame_pixels() {
  return frame_pixels;
}

size_t ThermalCamera::get_width() {
  return width;
}

size_t ThermalCamera::get_height() {
  return height;
}

psw ThermalCamera::get_camera_ptr() {
  return camera;
}
