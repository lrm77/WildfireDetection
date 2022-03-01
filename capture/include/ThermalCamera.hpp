#ifndef THERMAL_CAMERA_H
#define THERMAL_CAMERA_H

#include <seekware/seekware.h>
#include "Camera.hpp"

#include <string>
#include <thread>
#include <mutex>
#include <unordered_map>

#define NUM_CAMS 3

class ThermalCamera : public Camera
{
private:
     /* Private Member Variables */

     std::string serial_number;   // Serial number of physical camera
     psw camera;                  // Pointer to physical camera
     uint16_t *thermography_data; // Pointer to thermography frame buffer
     size_t frame_pixels;         // Number of pixels in a captured frame
     size_t width;                // Number of pixels in a captured frame
     size_t height;               // Number of pixels in a captured frame

     /* Private Static Variables */

     static int num_cams_found;                                 // Number of physical cameras connected
     static bool initialized;                                   // Holds true when cameras are properly found
     static psw cam_list[NUM_CAMS];                             // List of connected cameras
     static int next_camera_id;                                 // Holds next unique camera ID
     static std::unordered_map<std::string, std::string> names; // Stores names of physical cameras
     static std::string name_file;                              // Stores name of file containing names

     /* Private Static Functions */

     /**
      * Prints information on physical thermal camera device.
      * Adapted from Seek Thermal, Inc.
      */
     static void print_fw_info(psw camera);

     /**
         * Generates and returns a unique name for a ThermalCamera instance.
         */
     static void set_name(psw camera);

     /**
         * Opens an available camera and returns a pointer to the 
         * devices information struct.
         * 
         * Also performs initialization if necessary to find available cameras.
         */
     static psw get_camera();

     /**
         * Initializes settings for a seekware thermal camera
         */
     static void initialize_camera(psw camera);

     /**
         * Finds all connected cameras and stores them in cam_list
         */
     static void init();
     /** 
      * Initializes the dictionary of names from the startup file
      */
     static void read_names();
     /** 
      * Initializes the dictionary of names from the startup file
      */
     static void initialize_names();
     /** 
      * Stores the names in the dictionary to a file
      */
     static void write_names();
     /** 
         * Writes thermography data into a csv file with the specified filename.
         */
     static int write_thermography_data_csv(psw camera, std::string filename, uint16_t *thermography_data);

public:
     /* Public Member Functions */

     /** 
      * Creates and initializes a ThermalCamera instance
      */
     ThermalCamera();

     /**
      * Destructs instace of a ThermalCamera and frees memory
      */
     ~ThermalCamera();

     /**
     * Captures a thermography image and writes the frame to a unique file
     */
     void capture_image(std::string filename);

     /**
     * Returns frame pixels for the camera
     */
     size_t get_frame_pixels();

     /**
     * Returns frame width
     */
     size_t get_width();

     /**
     * Returns frame height
     */
     size_t get_height();

     /**
     * Returns pointer to the camera
     */
     psw get_camera_ptr();
};

#endif
