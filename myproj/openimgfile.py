# import the necessary packages
import shutil  # python's filestream lib
import requests  # a HTTP handler
import cv2  # openCV
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
imagedir1 = "img1.jpg"
imagedir2 = "img2.jpg"
imagedir3 = "img3.jpg"
imagedir4 = "img4.jpg"
imagedir5 = "img5.jpg"


url1 = "http://scada:scada@rno03p1nwoap01.teslamotors.com:7001/ec2/cameraThumbnail?cameraId=09ddfacb-ed1f-23bb-65a9-c42f9ccdfb11&time=latest&rotate=180&imageFormat=jpg&roundMethod=after&aspectRatio=auto&format=json";


# class to run a background thread on a timer event
class InfiniteTimer:

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


class LoopImg:
    # function to get image for processing
    def __init__(self, url, imagenum, imagedir):  # initialise variables and class input arguments
        self.url = url
        self.imagenum = imagenum
        self.imagedir = imagedir
        self.width = 610
        self.height = 400
        self.image = None
        self.scaleX = 0
        self.scaleY = 0

    # function to update image in tk GUI
    def panelupdate(self):
        # grab a reference to the image panels
        global panelA, panelB, panelC, panelD, panelE
        # if the panels are None, initialize them
        if panelA is None or panelB is None or panelC is None or panelD is None or panelE is None:
            if self.imagenum == 1:
                panelA = Label(image=self.image)
                panelA.Image = self.image
                panelA.grid(row=0, column=0, padx=10, pady=10)
            elif self.imagenum == 2:
                panelB = Label(image=self.image)
                panelB.Image = self.image
                panelB.grid(row=0, column=1, padx=10, pady=10)
            elif self.imagenum == 3:
                panelC = Label(image=self.image)
                panelC.Image = self.image
                panelC.grid(row=0, column=2, padx=10, pady=10)
            elif self.imagenum == 4:
                panelD = Label(image=self.image)
                panelD.Image = self.image
                panelD.grid(row=1, column=0, padx=10, pady=10)
            elif self.imagenum == 5:
                panelE = Label(image=self.image)
                panelE.Image = self.image
                panelE.grid(row=1, column=1, padx=10, pady=10)

        # otherwise, update the image panels
        else:
            # update the panels
            if self.imagenum == 1:
                panelA.configure(image=self.image, width=self.scaleX, height=self.scaleY)
                panelA.Image = self.image
            elif self.imagenum == 2:
                panelB.configure(image=self.image, width=self.scaleX, height=self.scaleY)
                panelB.Image = self.image
            elif self.imagenum == 3:
                panelC.configure(image=self.image, width=self.scaleX, height=self.scaleY)
                panelC.Image = self.image
            elif self.imagenum == 4:
                panelD.configure(image=self.image, width=self.scaleX, height=self.scaleY)
                panelD.Image = self.image
            elif self.imagenum == 5:
                panelE.configure(image=self.image, width=self.scaleX, height=self.scaleY)
                panelE.Image = self.image

    # function to get an image from url and copy to path
    def copy_urlimg_to_path(self):
        response = requests.get(self.url, stream=True)  # get URL response
        if response.status_code == 200:  # make sure we got a response
            with open(self.imagedir, 'wb') as out_file:  # with is python's equivalent of a try catch block
                shutil.copyfileobj(response.raw, out_file)  # use shutil to copy the raw response (aka the image) into the file path
        del response

    # function to rescale openCV window
    def rescalewindow(self):
        windowdimensions = self.width, self.height  # set my dimensions
        xscale = windowdimensions[0] / self.image.shape[1]  # get scale factor based on image size X
        yscale = windowdimensions[1] / self.image.shape[0]  # get scale factor based on image size Y
        scale = min(xscale, yscale)  # get the minimum value of x and y scale
        newwidth = int(self.image.shape[1] * scale)  # insert scaling
        newheight = int(self.image.shape[0] * scale)  # insert scaling
        cv2.namedWindow('Image 1', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Image 1', newwidth, newheight)

    # function to rescale tk GUI window
    def rescaleimg(self):
        windowdimensions = self.width, self.height  # set my dimensions
        xscale = windowdimensions[0] / self.image.shape[1]  # get scale factor based on image size X
        yscale = windowdimensions[1] / self.image.shape[0]  # get scale factor based on image size Y
        scale = min(xscale, yscale)  # get the minimum value of x and y scale
        newwidth = int(self.image.shape[1] * scale)  # insert scaling
        newheight = int(self.image.shape[0] * scale)  # insert scaling
        return newwidth, newheight

    def main(self):
        # copy file to path
        self.copy_urlimg_to_path()
        self.image = cv2.imread(self.imagedir)  # read file
        img = self.image
        self.scaleX, self.scaleY = self.rescaleimg()  # get scaling proportions
        # OpenCV represents images in BGR order; however PIL represents
        # images in RGB order, so we need to swap the channels
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        # convert the images to PIL format...
        self.image = Image.fromarray(self.image)
        # resize image
        self.image = self.image.resize((self.scaleX, self.scaleY), Image.ANTIALIAS)
        # ...and then convert to ImageTk format
        self.image = ImageTk.PhotoImage(self.image)
        self.panelupdate()
        # rescalewindow(640, 420, img)  # scale the display
        # cv2.imshow('Image 1', img)
        # cv2.waitKey(500)  # keep image for 500ms

    def run(self):
        img_thread1 = InfiniteTimer(0.5, self.main)
        img_thread1.start()


def main():
    # start timer threads
    imgInst1 = LoopImg(url1, 1, imagedir1)
    imgInst1.run();
    imgInst2 = LoopImg(url1, 2, imagedir2)
    imgInst2.run();
    imgInst3 = LoopImg(url1, 3, imagedir3)
    imgInst3.run();
    imgInst4 = LoopImg(url1, 4, imagedir4)
    imgInst4.run();
    imgInst5 = LoopImg(url1, 5, imagedir5)
    imgInst5.run();

    # kick off the GUI
    root.mainloop()


if __name__ == "__main__":  # define main function
    main()
