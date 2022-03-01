#ifndef CAMERA_HPP
#define CAMERA_HPP

#include <seekware/seekware.h>

#include <string>
#include <thread>
#include <mutex>
#include <unordered_map>
#include <sstream>

class Camera
{
protected:
     /* Private Member Variables */

     std::string name; // Unique name for ThermalCamera Instance
     std::mutex m;     // Mutex for thread safe capture
     std::string filename;
     // struct args {
     //      Camera* instance;
     //      std::string filename;
     // };

     /* Private Static Functions */

public:
     /**
         * Captures a thermography image and writes the frame to a unique file
         */
     virtual void capture_image(std::string filename) = 0;

     /**
         * Generats a file name to store a frame thermography image data
         * The output filename is of the form <name>_<timestamp>
         * where <name> is the unique Camera instance name 
         * and <timestamp> is a timestamp of when the image was taken.
         */
     std::string generate_filename(std::string timestamp, std::string extension, std::string path = "logs/")
     {
          std::ostringstream os;
          os << path << "/" << this->name << "_" << timestamp << extension;
          filename = os.str();
          return os.str();
     }

     /**
      * Returns current filename
      */
     std::string get_filename() {
          return filename;
     }
     
    /** 
     * Returns the name of the camera
     */
    std::string get_name() {
	return name;
    }

     /**
      * Forms an error message given the camera name and the input message
      */
     static std::string error(std::string msg, std::string name)
     {
          std::ostringstream os;
          os << "Error: " << name << ":\n";
          os << "\t" << msg << "\n";
          return os.str();
     }

     class CameraException : public std::exception
     {
          std::string msg;

     public:
          CameraException(std::string msg) : msg(msg) {}
          const char *what() const throw() { return msg.c_str(); }
     };
};

#endif
