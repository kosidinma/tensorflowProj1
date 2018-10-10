# import the necessary packages
import shutil  # python's filestream lib
import requests  # a HTTP handler
import cv2  # openCV
from threading import Thread  # we're using threads
from tkinter import *
from PIL import Image, ImageTk
from threading import Timer  # we use threads


# initialize the window toolkit along with the two image panels
root = Tk()
#root.geometry("800x420")
panelA = None
panelB = None
panelC = None
panelD = None
panelE = None


class InfiniteTimer:
    """A Timer class that does not stop, unless you want it to."""

    def __init__(self, seconds, target):  # initialise variables and class input arguments
        self._should_continue = False
        self.is_running = False
        self.seconds = seconds
        self.target = target
        self.thread = None

    def _handle_target(self):
        self.is_running = True
        self.target()
        self.is_running = False
        self._start_timer()

    def _start_timer(self):
        if self._should_continue:  # Code could have been running when cancel was called.
            self.thread = Timer(self.seconds, self._handle_target)
            self.thread.start()

    def start(self):
        if not self._should_continue and not self.is_running:
            self._should_continue = True
            self._start_timer()
        else:
            print("Timer already started or running, please wait if you're restarting.")

    def cancel(self):
        if self.thread is not None:
            self._should_continue = False  # Just in case thread is running and cancel fails.
            self.thread.cancel()
        else:
            print("Timer never started or failed to initialize.")


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


def rescaleimg(width, height, image):
    windowdimensions = width, height  # set my dimensions
    xscale = windowdimensions[0] / image.shape[1]  # get scale factor based on image size X
    yscale = windowdimensions[1] / image.shape[0]  # get scale factor based on image size Y
    scale = min(xscale, yscale)  # get the minimum value of x and y scale
    newwidth = int(image.shape[1] * scale)  # insert scaling
    newheight = int(image.shape[0] * scale)  # insert scaling
    return newwidth, newheight


def loopImg():
    # copy file to path
    copy_urlimg_to_path("http://scada:scada@rno03p1nwoap01.teslamotors.com:7001/ec2/cameraThumbnail?cameraId=09ddfacb-ed1f-23bb-65a9-c42f9ccdfb11&time=latest&rotate=180&imageFormat=jpg&roundMethod=after&aspectRatio=auto&format=json")
    img = cv2.imread("img.jpg") # read file
    scaleX, scaleY = rescaleimg(610, 400, img)  # get scaling proportions
    # OpenCV represents images in BGR order; however PIL represents
    # images in RGB order, so we need to swap the channels
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # convert the images to PIL format...
    img = Image.fromarray(img)
    # resize image
    img = img.resize((scaleX, scaleY), Image.ANTIALIAS)
    # ...and then convert to ImageTk format
    img = ImageTk.PhotoImage(img)
    panelupdate(img, scaleX, scaleY)
    # rescalewindow(640, 420, img)  # scale the display
    # cv2.imshow('Image 1', img)
    # cv2.waitKey(500)  # keep image for 500ms


def panelupdate(image, panelwidth, panelheight):
    # grab a reference to the image panels
    global panelA, panelB, panelC, panelD, panelE
    # if the panels are None, initialize them
    if panelA is None or panelB is None or panelC is None or panelD is None or panelE is None:
        # the first panel will store our original image
        panelA = Label(image=image)
        panelA.Image = image
        panelA.grid(row=0, column=0, padx=10, pady=10)

        # while the second panel will store the edge map
        panelB = Label(image=image)
        panelB.Image = image
        panelB.grid(row=0, column=1, padx=10, pady=10)

        panelC = Label(image=image)
        panelC.Image = image
        panelC.grid(row=0, column=2, padx=10, pady=10)

        panelD = Label(image=image)
        panelD.Image = image
        panelD.grid(row=1, column=0, padx=10, pady=10)

        panelE = Label(image=image)
        panelE.Image = image
        panelE.grid(row=1, column=1, padx=10, pady=10)

    # otherwise, update the image panels
    else:
        # update the panels
        panelA.configure(image=image, width=panelwidth, height=panelheight)
        panelB.configure(image=image, width=panelwidth, height=panelheight)
        panelC.configure(image=image, width=panelwidth, height=panelheight)
        panelD.configure(image=image, width=panelwidth, height=panelheight)
        panelE.configure(image=image, width=panelwidth, height=panelheight)
        panelA.Image = image
        panelB.Image = image
        panelC.Image = image
        panelD.Image = image
        panelE.Image = image


def main():
    # start timer
    t = InfiniteTimer(0.1, loopImg)  # run thread every 0.5 seconds
    t.start()
    # kick off the GUI
    root.mainloop()


if __name__ == "__main__":  # define main function
    main()
