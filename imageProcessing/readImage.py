import cv2

# pip install opencv-python

def toDegC(pixelValue):
    """ Converts a thermography value to a temperature in degrees C. 
    Conversion from Seekware documentation.
    Args:
        pixelValue (int): 16-bit thermography value capured from the camera
    Returns:
        float: Temperature in Degrees C
    """
    return pixelValue/64.0 - 40

def readMeasuredTemp(im):
    """Reads the temperature value of the captured by the IR camera. 
       Takes the maximum value of a center block of pixels to account 
       for errors aiming the camera.

    Args:
        im: Array of pixel values from a grayscale image captured by IR camera

    Returns:
        float: Measured temperature in degrees C of the thermal target
    """
    # Number of pixels on each side of the center to check
    radius = 35 
    # Get center point of image
    height, width = im.shape
    centerY = height//2
    centerX = width//2
    # Get the maximum value of the center block of pixels
    max = 0
    for i in range(centerY-radius, centerY+radius+1):
        for j in range(centerX-radius, centerX+radius):
            if im[i, j] > max:
                max = im[i, j]
    return max

# Source folder for images
folder = '/Users/lukemajors/Documents/School/Spring 2022/Photography/imageDataFocused/'

# Name of output file to write data
filename = 'focused.csv'
file = open(filename, 'w')

# Temperatures tested
#temps = ['100c', '200c', '400c']
temps = ['200c']
# Set up distances array
# Distances in range 20 - 240 with increment of 20
distances = []
for d in range (20, 260, 20):
    distances.append(str(d) + 'ft')
path = "/Users/lukemajors/Documents/School/Spring 2022/Photography/imageData/Testing_02-23-22_100c_20ft_3.png"

distances = []
for d in range(4, 38, 2):
    distances.append(str(d) + 'ft')

for temp in temps:
    for dist in distances:
        trialTemps = []
        for i in range(10): # There were 10 images taken at each location/temperature
            name = 'Testing_02-23-22_' + temp + '_' + dist + '_' + str(i) + '.png'
            im = cv2.imread(folder + name, -1)
            if im is None:
                print("Image " + name + " could not be read.")
                # f = open("faulty.txt", 'a')
                # f.write(name+'\n')
                # f.close()
                continue
            trialTemps.append(readMeasuredTemp(im))
        pixelVal = sum(trialTemps) // len(trialTemps)
        measuredTemp = toDegC(pixelVal)
        # Write the data to the output file. Get average of the 10 trials
        file.write(temp + ', ' + dist + ', ' + str(measuredTemp) + ', ' + str(pixelVal) + '\n')
file.close()
