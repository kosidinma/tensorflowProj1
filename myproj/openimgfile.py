# import the necessary packages
import shutil  # python's filestream lib
import requests  # a HTTP handler
import cv2  # openCV
from threading import Thread  # we're using threads
import keyboard  # Using module keyboard

class InfiniteLoop(Thread):
    def __init__(self, target):  # initialise variables and class input arguments
        Thread.__init__(self)
        self.running = True
        self.target = target

    def run(self):
        while self.running:
            self.target()

    def stop(self):
        self.running = False

# function to get an image from url and copy to path
def copy_urlimg_to_path(url):
    response = requests.get(url, stream=True) #get URL response
    if response.status_code == 200: # make sure we got a response
        with open('img.jpg', 'wb') as out_file: #with is python's equivalent of a try catch block
            shutil.copyfileobj(response.raw, out_file) # use shutil to copy the raw response (aka the image) into the file path
    del response


#function to rescale openCV window
def rescalewindow(width, height, image):
    windowdimensions = width, height  # set my dimensions
    xscale = windowdimensions[0] / image.shape[1]  # get scale factor based on image size X
    yscale = windowdimensions[1] / image.shape[0]  # get scale factor based on image size Y
    scale = min(xscale, yscale)  # get the minimum value of x and y scale
    newwidth = int(image.shape[1] * scale)  # insert scaling
    newheight = int(image.shape[0] * scale)  # insert scaling
    cv2.namedWindow('Image 1', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Image 1', newwidth, newheight)


def loopImg():
    # copy file to path
    copy_urlimg_to_path("http://scada:scada@rno03p1nwoap01.teslamotors.com:7001/ec2/cameraThumbnail?cameraId=09ddfacb-ed1f-23bb-65a9-c42f9ccdfb11&time=latest&rotate=180&imageFormat=jpg&roundMethod=after&aspectRatio=auto&format=json")
    img = cv2.imread("img.jpg") # read file
    rescalewindow(640, 420, img) # scale the display
    cv2.imshow('Image 1', img)
    cv2.waitKey(500)  # keep image for 500ms
    # cv2.destroyAllWindows()


def main():
    # start timer
    t = InfiniteLoop(loopImg)
    t.start()
    if keyboard.is_pressed('q'):  # if key 'q' is pressed
        t.stop()


if __name__ == "__main__":  # define main function
    main()
