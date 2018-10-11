# import the necessary packages
import shutil  # python's filestream lib
import requests  # a HTTP handler
import cv2  # openCV
from tkinter import *
from PIL import Image, ImageTk
from threading import Timer  # we use threads
import os
import os.path
import time
from functools import partial


# initialize the window toolkit along with the two image panels
root = Tk()
#root.geometry("800x420")
panelA = None
panelB = None
panelC = None
panelD = None
panelE = None

btn1_good = None
btn1_bad = None
btn2_good = None
btn2_bad = None
btn3_good = None
btn3_bad = None
btn4_good = None
btn4_bad = None
btn5_good = None
btn5_bad = None
btn1_test = None
txt1_test = None
btn1_addgood = None
btn1_addbad = None
btn2_test = None
txt2_test = None
btn2_addgood = None
btn2_addbad = None
btn3_test = None
txt3_test = None
btn3_addgood = None
btn3_addbad = None
btn4_test = None
txt4_test = None
btn4_addgood = None
btn4_addbad = None
btn5_test = None
txt5_test = None
btn5_addgood = None
btn5_addbad = None

testmodeCtrl = 0

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
                panelA.grid(row=0, column=0, rowspan=3, columnspan=2, padx=10, pady=10)
            elif self.imagenum == 2:
                panelB = Label(image=self.image)
                panelB.Image = self.image
                panelB.grid(row=0, column=3, rowspan=3, columnspan=2, padx=10, pady=10)
            elif self.imagenum == 3:
                panelC = Label(image=self.image)
                panelC.Image = self.image
                panelC.grid(row=0, column=6, rowspan=3, columnspan=2, padx=10, pady=10)
            elif self.imagenum == 4:
                panelD = Label(image=self.image)
                panelD.Image = self.image
                panelD.grid(row=5, column=0, rowspan=3, columnspan=2, padx=10, pady=10)
            elif self.imagenum == 5:
                panelE = Label(image=self.image)
                panelE.Image = self.image
                panelE.grid(row=5, column=3, rowspan=3, columnspan=2, padx=10, pady=10)

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
            # The with statement simplifies exception handling by encapsulating common preparation and cleanup tasks.
            # In addition, it will automatically close the file. The with statement provides a way for ensuring
            # that a clean-up is always used.
            with open(self.imagedir, 'wb') as out_file:
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
        img_thread = InfiniteTimer(0.5, self.main)
        img_thread.start()


def copytofolder(myimgpath, folderpath):
    # path to folders of image, timestamp added to give image a distinct name
    myimgpath = os.getcwd() + "/" + myimgpath
    print(myimgpath)
    folderpath = os.getcwd() + '/training_images/' + folderpath + '/image' + str(time.time()) + ".jpg"
    os.makedirs(os.path.dirname(folderpath), exist_ok=True)  # create directory if it doesn't exist
    # The with statement simplifies exception handling by encapsulating common preparation and cleanup tasks.
    # In addition, it will automatically close the file. The with statement provides a way for ensuring
    # that a clean-up is always used.
    os.rename(myimgpath, folderpath)


def classificationbtn_init_():
    # get global references
    global btn1_bad, btn1_good, btn2_bad, btn2_good, btn3_bad, btn3_good, btn4_bad, btn4_good, btn5_bad, btn5_good, \
        panelA, panelB, panelC, panelD, panelE
    # initialize classification buttons
    # WE USE THE "PARTIAL" KEYWORD TO PASS IN ARGS WITH A FUNCTION WHEN ONLY FUNCTION NAME IS EXPECTED
    btn1_good = Button(root, text="GOOD", width=30, command=partial(copytofolder, "img1.jpg", "goodFolder1"))
    btn1_bad = Button(root, text="BAD", width=30, command=partial(copytofolder, "img1.jpg", "badFolder1"))
    # img2
    btn2_good = Button(root, text="GOOD", width=30, command=partial(copytofolder, "img2.jpg", "goodFolder2"))
    btn2_bad = Button(root, text="BAD", width=30, command=partial(copytofolder, "img2.jpg", "badFolder2"))
    # img3
    btn3_good = Button(root, text="GOOD", width=30, command=partial(copytofolder, "img3.jpg", "goodFolder3"))
    btn3_bad = Button(root, text="BAD", width=30, command=partial(copytofolder, "img3.jpg", "badFolder3"))
    # img4
    btn4_good = Button(root, text="GOOD", width=30, command=partial(copytofolder, "img4.jpg", "goodFolder4"))
    btn4_bad = Button(root, text="BAD", width=30, command=partial(copytofolder, "img4.jpg", "badFolder4"))
    # img5
    btn5_good = Button(root, text="GOOD", width=30, command=partial(copytofolder, "img5.jpg", "goodFolder5"))
    btn5_bad = Button(root, text="BAD", width=30, command=partial(copytofolder, "img5.jpg", "badFolder5"))


def testbtn_init_():
    # get global references
    global btn1_test, txt1_test, btn1_addgood, btn1_addbad, btn2_test, txt2_test, btn2_addgood, btn2_addbad, btn3_test,\
        txt3_test, btn3_addgood, btn3_addbad, btn4_test, txt4_test, btn4_addgood, btn4_addbad, btn5_test, txt5_test,\
        btn5_addgood, btn5_addbad
    resultstr1 = ""
    resultstr2 = ""
    resultstr3 = ""
    resultstr4 = ""
    resultstr5 = ""

    # initialize test buttons
    btn1_test = Button(root, text="TEST", width=30, command="")
    txt1_test = Label(root, text=resultstr1)
    btn1_addgood = Button(root, text="ADD TO GOOD", width=30, command="")
    btn1_addbad = Button(root, text="ADD TO BAD", width=30, command="")
    # img2
    btn2_test = Button(root, text="TEST", width=30, command="")
    txt2_test = Label(root, text=resultstr2)
    btn2_addgood = Button(root, text="ADD TO GOOD", width=30, command="")
    btn2_addbad = Button(root, text="ADD TO BAD", width=30, command="")
    # img3
    btn3_test = Button(root, text="TEST", width=30, command="")
    txt3_test = Label(root, text=resultstr3)
    btn3_addgood = Button(root, text="ADD TO GOOD", width=30, command="")
    btn3_addbad = Button(root, text="ADD TO BAD", width=30, command="")
    # img4
    btn4_test = Button(root, text="TEST", width=30, command="")
    txt4_test = Label(root, text=resultstr4)
    btn4_addgood = Button(root, text="ADD TO GOOD", width=30, command="")
    btn4_addbad = Button(root, text="ADD TO BAD", width=30, command="")
    # img5
    btn5_test = Button(root, text="TEST", width=30, command="")
    txt5_test = Label(root, text=resultstr5)
    btn5_addgood = Button(root, text="ADD TO GOOD", width=30, command="")
    btn5_addbad = Button(root, text="ADD TO BAD", width=30, command="")


def showclassificationbtns():
    # get global references
    global btn1_bad, btn1_good, btn2_bad, btn2_good, btn3_bad, btn3_good, btn4_bad, btn4_good, btn5_bad, btn5_good
    # btn1_good = Button(root, text="GOOD", width=30, command="")
    btn1_good.grid(row=3, column=0, padx="10", pady="10")
    # btn1_bad = Button(root, text="BAD", width=30, command="")
    btn1_bad.grid(row=3, column=1, padx="10", pady="10")
    # img2
    # btn2_good = Button(root, text="GOOD", width=30, command="")
    btn2_good.grid(row=3, column=3, padx="10", pady="10")
    # btn2_bad = Button(root, text="BAD", width=30, command="")
    btn2_bad.grid(row=3, column=4, padx="10", pady="10")
    # img3
    # btn3_good = Button(root, text="GOOD", width=30, command="")
    btn3_good.grid(row=3, column=6, padx="10", pady="10")
    # btn3_bad = Button(root, text="BAD", width=30, command="")
    btn3_bad.grid(row=3, column=7, padx="10", pady="10")
    # img4
    # btn4_good = Button(root, text="GOOD", width=30, command="")
    btn4_good.grid(row=8, column=0, padx="10", pady="10")
    # btn4_bad = Button(root, text="BAD", width=30, command="")
    btn4_bad.grid(row=8, column=1, padx="10", pady="10")
    # img5
    # btn5_good = Button(root, text="GOOD", width=30, command="")
    btn5_good.grid(row=8, column=3, padx="10", pady="10")
    # btn5_bad = Button(root, text="BAD", width=30, command="")
    btn5_bad.grid(row=8, column=4, padx="10", pady="10")


def hideclassificationbtns():
    # get global references
    global btn1_bad, btn1_good, btn2_bad, btn2_good, btn3_bad, btn3_good, btn4_bad, btn4_good, btn5_bad, btn5_good
    btn1_good.grid_forget()
    btn1_bad.grid_forget()
    btn2_good.grid_forget()
    btn2_bad.grid_forget()
    btn3_good.grid_forget()
    btn3_bad.grid_forget()
    btn4_good.grid_forget()
    btn4_bad.grid_forget()
    btn5_good.grid_forget()
    btn5_bad.grid_forget()


def showtestbtns():
    # get global references
    global btn1_test, btn2_test, btn3_test, btn4_test, btn5_test
    btn1_test.grid(row=3, column=0, padx="10", pady="10")
    btn2_test.grid(row=3, column=3, padx="10", pady="10")
    btn3_test.grid(row=3, column=6, padx="10", pady="10")
    btn4_test.grid(row=8, column=0, padx="10", pady="10")
    btn5_test.grid(row=8, column=3, padx="10", pady="10")


def hidetestbtns():
    # get global references
    # get global references
    global btn1_test, txt1_test, btn1_addgood, btn1_addbad, btn2_test, txt2_test, btn2_addgood, btn2_addbad, btn3_test,\
        txt3_test, btn3_addgood, btn3_addbad, btn4_test, txt4_test, btn4_addgood, btn4_addbad, btn5_test, txt5_test, \
        btn5_addgood, btn5_addbad
    btn1_test.grid_forget()
    txt1_test.grid_forget()
    btn1_addgood.grid_forget()
    btn1_addbad.grid_forget()
    btn2_test.grid_forget()
    txt2_test.grid_forget()
    btn2_addgood.grid_forget()
    btn2_addbad.grid_forget()
    btn3_test.grid_forget()
    txt3_test.grid_forget()
    btn3_addgood.grid_forget()
    btn3_addbad.grid_forget()
    btn4_test.grid_forget()
    txt4_test.grid_forget()
    btn4_addgood.grid_forget()
    btn4_addbad.grid_forget()
    btn5_test.grid_forget()
    txt5_test.grid_forget()
    btn5_addgood.grid_forget()
    btn5_addbad.grid_forget()



def show_hide_btns():
    # get global references
    global testmodeCtrl, btn1_test, txt1_test, lbl1_test, btn2_test, txt2_test, lbl2_test, btn3_test, txt3_test, \
        lbl3_test, btn4_test, txt4_test, lbl4_test, btn5_test, txt5_test, lbl5_test
    # add buttons
    # width is in %
    # img1
    if testmodeCtrl.get() == 0:
        showclassificationbtns()
        hidetestbtns()
    else:
        hideclassificationbtns()
        showtestbtns()


def main():
    # get global references
    global testmodeCtrl

    # set urls
    url1 = "http://scada:scada@rno03p1nwoap01.teslamotors.com:7001/ec2/cameraThumbnail?cameraId=09ddfacb-ed1f-23bb-65a9-c42f9ccdfb11&time=latest&rotate=180&imageFormat=jpg&roundMethod=after&aspectRatio=auto&format=json"
    url2 = "http://scada:scada@rno03p1nwoap01.teslamotors.com:7001/ec2/cameraThumbnail?cameraId=a30471e7-ebdd-ddb3-06f6-d4b465e0dfae&time=latest&rotate=0&imageFormat=jpg&roundMethod=after&aspectRatio=auto&format=json"
    url3 = "http://scada:scada@rno03p1nwoap01.teslamotors.com:7001/ec2/cameraThumbnail?cameraId=238eec33-0fe4-97b5-1013-9e503b9b5882&time=latest&rotate=0&imageFormat=jpg&roundMethod=after&aspectRatio=auto&format=json"
    url4 = "http://scada:scada@rno03p1nwoap01.teslamotors.com:7001/ec2/cameraThumbnail?cameraId=dd18d158-c192-9e19-3b67-05e20742d105&time=latest&rotate=0&imageFormat=jpg&roundMethod=after&aspectRatio=auto&format=json"
    url5 = "http://scada:scada@rno03p1nwoap01.teslamotors.com:7001/ec2/cameraThumbnail?cameraId=75061ddd-ba25-286a-be39-dcbce5fb5e67&time=latest&rotate=0&imageFormat=jpg&roundMethod=after&aspectRatio=auto&format=json"

    # set image directories
    imagedir1 = "img1.jpg"
    imagedir2 = "img2.jpg"
    imagedir3 = "img3.jpg"
    imagedir4 = "img4.jpg"
    imagedir5 = "img5.jpg"

    testmodeCtrl = IntVar()
    mylbl = "Toggle Test Mode"
    # start timer threads
    imgInst1 = LoopImg(url1, 1, imagedir1)
    imgInst1.run()
    imgInst2 = LoopImg(url2, 2, imagedir2)
    imgInst2.run()
    imgInst3 = LoopImg(url3, 3, imagedir3)
    imgInst3.run()
    imgInst4 = LoopImg(url4, 4, imagedir4)
    imgInst4.run()
    imgInst5 = LoopImg(url5, 5, imagedir5)
    imgInst5.run()
    # initialize classification buttons
    classificationbtn_init_()
    # initialize test buttons
    testbtn_init_()
    # function to show/hide buttons on first try
    show_hide_btns()
    # checkbox to show/hide buttons
    Checkbutton(root, text=mylbl, variable=testmodeCtrl, command=show_hide_btns).grid(row=9, column=0, sticky=W, padx="10", pady="20")

    # kick off the GUI
    root.mainloop()


if __name__ == "__main__":  # define main function
    main()
