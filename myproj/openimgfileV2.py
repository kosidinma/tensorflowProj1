# import the necessary packages
import shutil  # python's filestream lib
import requests  # a HTTP handler
import cv2  # openCV
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from threading import Timer  # we use threads
import os
import os.path
import time
from functools import partial
import tensorflow as tf
import numpy as np
from threading import Thread  # we're using threads

# module-level variables ##############################################################################################
RETRAINED_LABELS_TXT_FILE_LOC = os.getcwd() + "/" + "retrained_labels.txt"
RETRAINED_GRAPH_PB_FILE_LOC = os.getcwd() + "/" + "retrained_graph.pb"

TEST_IMAGES_DIR = os.getcwd() + "/test_images"

SCALAR_RED = (0.0, 0.0, 255.0)
SCALAR_BLUE = (255.0, 0.0, 0.0)
# initialize the window toolkit along with the two image panels
root = Tk()
root.title("Classification Software V 2.0")

# set root window to maximize screen
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))

statusbox = None  # pop up window


# image display stuff
panelA = None
panelB = None
panelC = None
panelD = None
panelE = None

# classification GUI stuff
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

# test GUI stuff
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

# Classification Wrong GUI stuff
btn1_unclassified = None
btn1_add_unclassified = None
btn2_unclassified = None
btn2_add_unclassified = None
btn3_unclassified = None
btn3_add_unclassified = None
btn4_unclassified = None
btn4_add_unclassified = None
btn5_unclassified = None
btn5_add_unclassified = None

# initialize check for button busy
btn1_good_busy = False
btn1_bad_busy = False
btn1_unclassified_busy = False
btn2_good_busy = False
btn2_bad_busy = False
btn2_unclassified_busy = False
btn3_good_busy = False
btn3_bad_busy = False
btn3_unclassified_busy = False
btn4_good_busy = False
btn4_bad_busy = False
btn4_unclassified_busy = False
btn5_good_busy = False
btn5_bad_busy = False
btn5_unclassified_busy = False

testmodeCtrl = 0


# file copy control thread class
class filecopyCtrl(Thread):
    def __init__(self, myimgpath, folderpath, btnindex):  # initialise variables and class input arguments
        Thread.__init__(self)
        self.running = True
        self.imagepath = myimgpath
        self.folderpath = folderpath
        self.btnindex = btnindex
        # A daemon thread will not prevent the application from exiting.
        # The program ends when all non-daemon threads (main thread included) are complete.
        self.setDaemon(True)

    def run(self):  # try to copy file and if it doesn't exist, keep retrying in thread
        while True:
            try:
                os.rename(self.imagepath, self.folderpath)
            except(OSError, IOError):
                continue
            print("Target not in use")
            setButtonBusy(False, self.btnindex)
            break


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
            # A daemon thread will not prevent the application from exiting.
            # The program ends when all non-daemon threads (main thread included) are complete.
            self.thread.setDaemon(True)
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
                panelD.grid(row=6, column=0, rowspan=3, columnspan=2, padx=10, pady=10)
            elif self.imagenum == 5:
                panelE = Label(image=self.image)
                panelE.Image = self.image
                panelE.grid(row=6, column=3, rowspan=3, columnspan=2, padx=10, pady=10)

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
        if self.image is not None:  # only update panel if resource exists
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

    def run(self):
        img_thread = InfiniteTimer(0.5, self.main)
        img_thread.start()


def getresult(myimgpath, num, textboxnum, testimgname):  # function to handle testing
    loadPromptPopUp("Testing....")  # notify status via textbox
    statusbox.update()  # update force update GUI
    time.sleep(0.1)  # make sure that GUI works
    hidetestbtns()  # don't allow any buttons to show while test is running
    time.sleep(1)  # make sure that GUI works
    copytofolder(myimgpath, num, testimgname, None)  # button index not needed for test
    if not checkIfNecessaryPathsAndFilesExist():  # don't test if files/folders are invalid
        return
    # end if
    # get a list of classifications from the labels file
    classifications = []
    # for each line in the label file . . .
    for currentLine in tf.gfile.GFile(RETRAINED_LABELS_TXT_FILE_LOC):
        # remove the carriage return
        classification = currentLine.rstrip()
        # and append to the list
        classifications.append(classification)
    # end for
    # load the graph from file
    with tf.gfile.FastGFile(RETRAINED_GRAPH_PB_FILE_LOC, 'rb') as retrainedGraphFile:
        # instantiate a GraphDef object
        graphDef = tf.GraphDef()
        # read in retrained graph into the GraphDef object
        graphDef.ParseFromString(retrainedGraphFile.read())
        # import the graph into the current default Graph, note that we don't need to be concerned with the return value
        _ = tf.import_graph_def(graphDef, name='')
    # end with
    # if the test image directory listed above is not valid, show an error message and bail
    if not os.path.isdir(TEST_IMAGES_DIR):
        print("the test image directory does not seem to be a valid directory, check file / directory paths")
        return
    # end if
    with tf.Session() as sess:
        # for each file in the test images directory . . .
        for fileName in os.listdir(TEST_IMAGES_DIR):
            # if the file does not end in .jpg or .jpeg (case-insensitive),
            # continue with the next iteration of the for loop
            # added by me: if file isn't the name I expect
            if not (fileName.lower().endswith(".jpg") or fileName.lower().endswith(".jpeg") or fileName.lower() == (testimgname + ".jpg")):
                continue
            # end if

            # get the file name and full path of the current image file
            imageFileWithPath = os.path.join(TEST_IMAGES_DIR, fileName)
            # attempt to open the image with OpenCV
            openCVImage = cv2.imread(imageFileWithPath)
            # if we were not able to successfully open the image, continue with the next iteration of the for loop
            if openCVImage is None:
                print("unable to open " + fileName + " as an OpenCV image")
                continue
            # end if
            # get the final tensor from the graph
            finalTensor = sess.graph.get_tensor_by_name('final_result:0')
            # convert the OpenCV image (numpy array) to a TensorFlow image
            tfImage = np.array(openCVImage)[:, :, 0:3]
            # run the network to get the predictions
            predictions = sess.run(finalTensor, {'DecodeJpeg:0': tfImage})
            # sort predictions from most confidence to least confidence
            sortedPredictions = predictions[0].argsort()[-len(predictions[0]):][::-1]
            # for each prediction . . .
            for prediction in sortedPredictions:
                strClassification = classifications[prediction]
                # if the classification (obtained from the directory name) ends with the letter "s",
                # remove the "s" to change from plural to singular
                if strClassification.endswith("s"):
                    strClassification = strClassification[:-1]
                # end if
                # get confidence, then get confidence rounded to 2 places after the decimal
                confidence = predictions[0][prediction]
                # for any prediction, show the confidence as a ratio to five decimal places
                textstr = strClassification + " (" + "{0:.5f}".format(confidence) + ")"
                break # kosy only wants one loop
            # end for
        # end for
    # end with
    showtestbtns()  # show the buttons again
    time.sleep(0.1)  # make sure that GUI works
    close_loadPromptPopUp()   # close the text box
    time.sleep(0.1)  # make sure that GUI works
    popup_test_result(textboxnum, textstr)
# end main


# sets button to busy or not busy and handles multiple clicking during processes
def setButtonBusy(state, btnIndx):
    global btn1_good_busy, btn1_bad_busy, btn1_unclassified_busy, btn2_good_busy, btn2_bad_busy, \
        btn2_unclassified_busy, btn3_good_busy, btn3_bad_busy, btn3_unclassified_busy, btn4_good_busy, \
        btn4_bad_busy, btn4_unclassified_busy, btn5_good_busy, btn5_bad_busy, btn5_unclassified_busy, btn1_bad, \
        btn1_good, btn2_bad, btn2_good, btn3_bad, btn3_good, btn4_bad, btn4_good, btn5_bad, btn5_good, \
        btn1_unclassified, btn2_unclassified, btn3_unclassified, btn4_unclassified, btn5_unclassified, \
        btn1_bad, btn1_good, btn2_bad, btn2_good, btn3_bad, btn3_good, btn4_bad, btn4_good, btn5_bad, btn5_good, \
        btn1_unclassified, btn2_unclassified, btn3_unclassified, btn4_unclassified, btn5_unclassified

    if not state:  # set as not busy and enable button
        if btnIndx == 1:
            btn1_good_busy = False
            btn1_good.config(state="normal")
        elif btnIndx == 2:
            btn1_bad_busy = False
            btn1_bad.config(state="normal")
        elif btnIndx == 3:
            btn1_unclassified_busy = False
            btn1_unclassified.config(state="normal")
        elif btnIndx == 4:
            btn2_good_busy = False
            btn2_good.config(state="normal")
        elif btnIndx == 5:
            btn2_bad_busy = False
            btn2_bad.config(state="normal")
        elif btnIndx == 6:
            btn2_unclassified_busy = False
            btn2_unclassified.config(state="normal")
        elif btnIndx == 7:
            btn3_good_busy = False
            btn3_good.config(state="normal")
        elif btnIndx == 8:
            btn3_bad_busy = False
            btn3_bad.config(state="normal")
        elif btnIndx == 9:
            btn3_unclassified_busy = False
            btn3_unclassified.config(state="normal")
        elif btnIndx == 10:
            btn4_good_busy = False
            btn4_good.config(state="normal")
        elif btnIndx == 11:
            btn4_bad_busy = False
            btn4_bad.config(state="normal")
        elif btnIndx == 12:
            btn4_unclassified_busy = False
            btn4_unclassified.config(state="normal")
        elif btnIndx == 13:
            btn5_good_busy = False
            btn5_good.config(state="normal")
        elif btnIndx == 14:
            btn5_bad_busy = False
            btn5_bad.config(state="normal")
        elif btnIndx == 15:
            btn5_unclassified_busy = False
            btn5_unclassified.config(state="normal")
    else:
        if btnIndx == 1:
            btn1_good_busy = True
            btn1_good.config(state=DISABLED)
        elif btnIndx == 2:
            btn1_bad_busy = True
            btn1_bad.config(state=DISABLED)
        elif btnIndx == 3:
            btn1_unclassified_busy = True
            btn1_unclassified.config(state=DISABLED)
        elif btnIndx == 4:
            btn2_good_busy = True
            btn2_good.config(state=DISABLED)
        elif btnIndx == 5:
            btn2_bad_busy = True
            btn2_bad.config(state=DISABLED)
        elif btnIndx == 6:
            btn2_unclassified_busy = True
            btn2_unclassified.config(state=DISABLED)
        elif btnIndx == 7:
            btn3_good_busy = True
            btn3_good.config(state=DISABLED)
        elif btnIndx == 8:
            btn3_bad_busy = True
            btn3_bad.config(state=DISABLED)
        elif btnIndx == 9:
            btn3_unclassified_busy = True
            btn3_unclassified.config(state=DISABLED)
        elif btnIndx == 10:
            btn4_good_busy = True
            btn4_good.config(state=DISABLED)
        elif btnIndx == 11:
            btn4_bad_busy = True
            btn4_bad.config(state=DISABLED)
        elif btnIndx == 12:
            btn4_unclassified_busy = True
            btn4_unclassified.config(state=DISABLED)
        elif btnIndx == 13:
            btn5_good_busy = True
            btn5_good.config(state=DISABLED)
        elif btnIndx == 14:
            btn5_bad_busy = True
            btn5_bad.config(state=DISABLED)
        elif btnIndx == 15:
            btn5_unclassified_busy = True
            btn5_unclassified.config(state=DISABLED)


# check button to busy or not busy
def buttonIsBusy(btnIndx):
    global btn1_good_busy, btn1_bad_busy, btn1_unclassified_busy, btn2_good_busy, btn2_bad_busy, \
        btn2_unclassified_busy, btn3_good_busy, btn3_bad_busy, btn3_unclassified_busy, btn4_good_busy, \
        btn4_bad_busy, btn4_unclassified_busy, btn5_good_busy, btn5_bad_busy, btn5_unclassified_busy

    if btnIndx == 1 and btn1_good_busy:
        return True
    elif btnIndx == 2 and btn1_bad_busy:
        return True
    elif btnIndx == 3 and btn1_unclassified_busy:
        return True
    elif btnIndx == 4 and btn2_good_busy:
        return True
    elif btnIndx == 5 and btn2_bad_busy:
        return True
    elif btnIndx == 6 and btn2_unclassified_busy:
        return True
    elif btnIndx == 7 and btn3_good_busy:
        return True
    elif btnIndx == 8 and btn3_bad_busy:
        return True
    elif btnIndx == 9 and btn3_unclassified_busy:
        return True
    elif btnIndx == 10 and btn4_good_busy:
        return True
    elif btnIndx == 11 and btn4_bad_busy:
        return True
    elif btnIndx == 12 and btn4_unclassified_busy:
        return True
    elif btnIndx == 13 and btn5_good_busy:
        return True
    elif btnIndx == 14 and btn5_bad_busy:
        return True
    elif btnIndx == 15 and btn5_unclassified_busy:
        return True
    else:
        return False


# function to put results in textbox
def updateResults(textboxnum, textstr):
    # get global references
    global btn1_test, btn2_test, btn3_test, btn4_test, btn5_test
    if textboxnum == 1:
        txt1_test["text"] = textstr
    elif textboxnum == 2:
        txt2_test["text"] = textstr
    elif textboxnum == 3:
        txt3_test["text"] = textstr
    elif textboxnum == 4:
        txt4_test["text"] = textstr
    elif textboxnum == 5:
        txt5_test["text"] = textstr


# unused....function to clear test results
def clearResults():
    # get global references
    global txt1_test, txt2_test, txt3_test, txt4_test, txt5_test
    txt1_test["text"] = ""
    txt2_test["text"] = ""
    txt3_test["text"] = ""
    txt4_test["text"] = ""
    txt5_test["text"] = ""


# function to make sure files exist before testing
def checkIfNecessaryPathsAndFilesExist():
    if not os.path.exists(TEST_IMAGES_DIR):
        print('')
        print('ERROR: TEST_IMAGES_DIR "' + TEST_IMAGES_DIR + '" does not seem to exist')
        print('Did you set up the test images?')
        print('')
        return False
    # end if
    if not os.path.exists(RETRAINED_LABELS_TXT_FILE_LOC):
        print('ERROR: RETRAINED_LABELS_TXT_FILE_LOC "' + RETRAINED_LABELS_TXT_FILE_LOC + '" does not seem to exist')
        return False
    # end if
    if not os.path.exists(RETRAINED_GRAPH_PB_FILE_LOC):
        print('ERROR: RETRAINED_GRAPH_PB_FILE_LOC "' + RETRAINED_GRAPH_PB_FILE_LOC + '" does not seem to exist')
        return False
    # end if
    return True


# function to copy stuff to folders
def copytofolder(myimgpath, num, folderpath, btnindex):
    # num = 1 ===> training path, anything else => testing path
    myimgpath = os.getcwd() + "/" + myimgpath
    if num == 1:  # append file
        if not buttonIsBusy(btnindex):  # if button already started a thread, do nothing
            setButtonBusy(True, btnindex)
            # path to folders of image, timestamp added to give image a distinct name
            folderpath = os.getcwd() + '/training_images/' + folderpath + '/image' + str(time.time()) + ".jpg"
            os.makedirs(os.path.dirname(folderpath), exist_ok=True)  # create directory if it doesn't exist
            # try...except to make sure file resource is not being used, if being used, handle using thread
            try:
                os.rename(myimgpath, folderpath)
            except(OSError, IOError):
                filecopyCtrlInst = filecopyCtrl(myimgpath, folderpath, btnindex)
                filecopyCtrlInst.run()
            else:
                setButtonBusy(False, btnindex)
        else:
            print("button" + str(btnindex) + " is busy")
    else:
        # for testing, use folderpath as image name straight, overwrite..no thread handling as it
        folderpath = os.getcwd() + '/test_images/' + folderpath + ".jpg"
        shutil.copy(myimgpath, folderpath)


# function to initialise clssification buttons
def classificationbtn_init_():

    # button index map:
    # btn1_good or add_good = 1
    # btn1_bad or add_bad = 2
    # btn1_unclassified or add_unclassified = 3
    # btn2_good or add_good = 4
    # btn2_bad or add_bad = 5
    # btn2_unclassified or add_unclassified = 6
    # btn3_good or add_good = 7
    # btn3_bad or add_bad = 8
    # btn3_unclassified or add_unclassified = 9
    # btn4_good or add_good = 10
    # btn4_bad or add_bad = 11
    # btn4_unclassified or add_unclassified = 12
    # btn5_good or add_good = 13
    # btn5_bad or add_bad = 14
    # btn5_unclassified or add_unclassified = 15

    # get global references...only required when writing
    global btn1_bad, btn1_good, btn2_bad, btn2_good, btn3_bad, btn3_good, btn4_bad, btn4_good, btn5_bad, btn5_good, \
        panelA, panelB, panelC, panelD, panelE, btn1_unclassified, btn2_unclassified, btn3_unclassified, \
        btn4_unclassified, btn5_unclassified
    # initialize classification buttons
    # WE USE THE "PARTIAL" KEYWORD TO PASS IN ARGS WITH A FUNCTION WHEN ONLY FUNCTION NAME IS EXPECTED
    btn1_good = Button(root, text="MARK AS SEATED", width=30, command=partial(copytofolder, "img1.jpg", 1, "goodFolder1", 1))
    btn1_bad = Button(root, text="MARK AS UNSEATED", width=30, command=partial(copytofolder, "img1.jpg", 1, "badFolder1", 2))
    btn1_unclassified = Button(root, text="USELESS", width=30,
                               command=partial(copytofolder, "img1.jpg", 1, "random_image", 3))
    # img2
    btn2_good = Button(root, text="MARK AS SEATED", width=30, command=partial(copytofolder, "img2.jpg", 1, "goodFolder2", 4))
    btn2_bad = Button(root, text="MARK AS UNSEATED", width=30, command=partial(copytofolder, "img2.jpg", 1, "badFolder2", 5))
    btn2_unclassified = Button(root, text="USELESS", width=30,
                               command=partial(copytofolder, "img2.jpg", 1, "random_image", 6))
    # img3
    btn3_good = Button(root, text="MARK AS SEATED", width=30, command=partial(copytofolder, "img3.jpg", 1, "goodFolder3", 7))
    btn3_bad = Button(root, text="MARK AS UNSEATED", width=30, command=partial(copytofolder, "img3.jpg", 1, "badFolder3", 8))
    btn3_unclassified = Button(root, text="USELESS", width=30,
                               command=partial(copytofolder, "img3.jpg", 1, "random_image", 9))
    # img4
    btn4_good = Button(root, text="MARK AS SEATED", width=30, command=partial(copytofolder, "img4.jpg", 1, "goodFolder4", 10))
    btn4_bad = Button(root, text="MARK AS UNSEATED", width=30, command=partial(copytofolder, "img4.jpg", 1, "badFolder4", 11))
    btn4_unclassified = Button(root, text="USELESS", width=30,
                               command=partial(copytofolder, "img4.jpg", 1, "random_image", 12))
    # img5
    btn5_good = Button(root, text="MARK AS SEATED", width=30, command=partial(copytofolder, "img5.jpg", 1, "goodFolder5", 13))
    btn5_bad = Button(root, text="MARK AS UNSEATED", width=30, command=partial(copytofolder, "img5.jpg", 1, "badFolder5", 14))
    btn5_unclassified = Button(root, text="USELESS", width=30,
                               command=partial(copytofolder, "img5.jpg", 1, "random_image", 15))


# function to initialise test buttons
def testbtn_init_():
    # button index map:
    # btn1_good or add_good = 1
    # btn1_bad or add_bad = 2
    # btn1_unclassified or add_unclassified = 3
    # btn2_good or add_good = 4
    # btn2_bad or add_bad = 5
    # btn2_unclassified or add_unclassified = 6
    # btn3_good or add_good = 7
    # btn3_bad or add_bad = 8
    # btn3_unclassified or add_unclassified = 9
    # btn4_good or add_good = 10
    # btn4_bad or add_bad = 11
    # btn4_unclassified or add_unclassified = 12
    # btn5_good or add_good = 13
    # btn5_bad or add_bad = 14
    # btn5_unclassified or add_unclassified = 15
    # get global references
    global btn1_test, btn2_test, btn3_test, btn4_test, btn5_test

    # initialize test buttons
    btn1_test = Button(root, text="TEST", width=30, command=partial(getresult, "img1.jpg", 0, 1, "testIMG1"))
    # img2
    btn2_test = Button(root, text="TEST", width=30, command=partial(getresult, "img2.jpg", 0, 2, "testIMG2"))
    # img3
    btn3_test = Button(root, text="TEST", width=30, command=partial(getresult, "img3.jpg", 0, 3, "testIMG3"))
    # img4
    btn4_test = Button(root, text="TEST", width=30, command=partial(getresult, "img4.jpg", 0, 4, "testIMG4"))
    # img5
    btn5_test = Button(root, text="TEST", width=30, command=partial(getresult, "img5.jpg", 0, 5, "testIMG5"))


# function to show classification buttons
def showclassificationbtns():
    # get global references
    global btn1_bad, btn1_good, btn2_bad, btn2_good, btn3_bad, btn3_good, btn4_bad, btn4_good, btn5_bad, btn5_good, \
        btn1_unclassified, btn2_unclassified, btn3_unclassified, btn4_unclassified, btn5_unclassified
    # imag1
    btn1_unclassified.grid(row=4, column=1, padx="10", pady="10")
    btn1_good.grid(row=3, column=0, padx="10", pady="10")
    btn1_bad.grid(row=3, column=1, padx="10", pady="10")
    # img2
    btn2_unclassified.grid(row=4, column=4, padx="10", pady="10")
    btn2_good.grid(row=3, column=3, padx="10", pady="10")
    btn2_bad.grid(row=3, column=4, padx="10", pady="10")
    # img3
    btn3_unclassified.grid(row=4, column=7, padx="10", pady="10")
    btn3_good.grid(row=3, column=6, padx="10", pady="10")
    btn3_bad.grid(row=3, column=7, padx="10", pady="10")
    # img4
    btn4_unclassified.grid(row=10, column=1, padx="10", pady="10")
    btn4_good.grid(row=9, column=0, padx="10", pady="10")
    btn4_bad.grid(row=9, column=1, padx="10", pady="10")
    # img5
    btn5_unclassified.grid(row=10, column=4, padx="10", pady="10")
    btn5_good.grid(row=9, column=3, padx="10", pady="10")
    btn5_bad.grid(row=9, column=4, padx="10", pady="10")


# function to hide classification buttons
def hideclassificationbtns():
    # get global references
    global btn1_bad, btn1_good, btn2_bad, btn2_good, btn3_bad, btn3_good, btn4_bad, btn4_good, btn5_bad, btn5_good, \
        btn1_unclassified, btn2_unclassified, btn3_unclassified, btn4_unclassified, btn5_unclassified
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
    btn1_unclassified.grid_forget()
    btn2_unclassified.grid_forget()
    btn3_unclassified.grid_forget()
    btn4_unclassified.grid_forget()
    btn5_unclassified.grid_forget()


# function to show test buttons
def showtestbtns():
    # get global references
    global btn1_test, btn2_test, btn3_test, btn4_test, btn5_test
    btn1_test.grid(row=3, column=0, columnspan=2, padx="10", pady="10")
    btn2_test.grid(row=3, column=3, columnspan=2, padx="10", pady="10")
    btn3_test.grid(row=3, column=6, columnspan=2, padx="10", pady="10")
    btn4_test.grid(row=9, column=0, columnspan=2, padx="10", pady="10")
    btn5_test.grid(row=9, column=3, columnspan=2, padx="10", pady="10")


# function to show test result popup features
def showresultfeatures(textboxnum):
    # get global references
    global txt1_test, btn1_addgood, btn1_addbad, txt2_test, btn2_addgood, btn2_addbad, txt3_test, btn3_addgood,\
        btn3_addbad, txt4_test, btn4_addgood, btn4_addbad, txt5_test, btn5_addgood, btn5_addbad, btn1_add_unclassified,\
        btn2_add_unclassified, btn3_add_unclassified, btn4_add_unclassified, btn5_add_unclassified
    if textboxnum == 1:
        txt1_test.grid(row=4, column=0, padx="10", pady="10", sticky=W + E + N + S)
        btn1_addgood.grid(row=3, column=1, padx="10", pady="10", sticky=W)
        btn1_addbad.grid(row=4, column=1, padx="10", pady="10", sticky=W)
        btn1_add_unclassified.grid(row=5, column=1, padx="10", pady="10", sticky=W)
    elif textboxnum == 2:
        txt2_test.grid(row=4, column=0, padx="10", pady="10", sticky=W + E + N + S)
        btn2_addgood.grid(row=3, column=1, padx="10", pady="10", sticky=W)
        btn2_addbad.grid(row=4, column=1, padx="10", pady="10", sticky=W)
        btn2_add_unclassified.grid(row=5, column=1, padx="10", pady="10", sticky=W)
    elif textboxnum == 3:
        txt3_test.grid(row=4, column=0, padx="10", pady="10", sticky=W + E + N + S)
        btn3_addgood.grid(row=3, column=1, padx="10", pady="10", sticky=W)
        btn3_addbad.grid(row=4, column=1, padx="10", pady="10", sticky=W)
        btn3_add_unclassified.grid(row=5, column=1, padx="10", pady="10", sticky=W)
    elif textboxnum == 4:
        txt4_test.grid(row=4, column=0, padx="10", pady="10", sticky=W + E + N + S)
        btn4_addgood.grid(row=3, column=1, padx="10", pady="10", sticky=W)
        btn4_addbad.grid(row=4, column=1, padx="10", pady="10", sticky=W)
        btn4_add_unclassified.grid(row=5, column=1, padx="10", pady="10", sticky=W)
    elif textboxnum == 5:
        txt5_test.grid(row=4, column=0, padx="10", pady="10", sticky=W + E + N + S)
        btn5_addgood.grid(row=3, column=1, padx="10", pady="10", sticky=W)
        btn5_addbad.grid(row=4, column=1, padx="10", pady="10", sticky=W)
        btn5_add_unclassified.grid(row=5, column=1, padx="10", pady="10", sticky=W)


# function to hide test buttons
def hidetestbtns():
    # get global references
    global btn1_test, txt1_test, btn1_addgood, btn1_addbad, btn2_test, txt2_test, btn2_addgood, btn2_addbad, btn3_test,\
        txt3_test, btn3_addgood, btn3_addbad, btn4_test, txt4_test, btn4_addgood, btn4_addbad, btn5_test, txt5_test, \
        btn5_addgood, btn5_addbad, btn1_add_unclassified, btn2_add_unclassified, btn3_add_unclassified, \
        btn4_add_unclassified, btn5_add_unclassified
    btn1_test.grid_forget()
    btn2_test.grid_forget()
    btn3_test.grid_forget()
    btn4_test.grid_forget()
    btn5_test.grid_forget()


# toggle control for hiding/showing buttons
def show_hide_btns():
    # get global references
    global testmodeCtrl
    # add buttons
    # width is in %
    # img1
    if testmodeCtrl.get() == 0:
        showclassificationbtns()
        hidetestbtns()
    else:
        hideclassificationbtns()
        showtestbtns()


# function to handle close button press
def on_close():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()


def rescaleimg(width, height, image):
    windowdimensions = width, height  # set my dimensions
    xscale = windowdimensions[0] / image.shape[1]  # get scale factor based on image size X
    yscale = windowdimensions[1] / image.shape[0]  # get scale factor based on image size Y
    scale = min(xscale, yscale)  # get the minimum value of x and y scale
    newwidth = int(image.shape[1] * scale)  # insert scaling
    newheight = int(image.shape[0] * scale)  # insert scaling
    return newwidth, newheight


def centerWindow(win, stateLocal):  # function to center tkinter window, state is either local or global
    global statusbox
    if stateLocal:
        # Gets the requested values of the height and width.
        windowWidth = win.winfo_reqwidth()
        windowHeight = win.winfo_reqheight()

        # Gets both half the screen width/height and window width/height
        positionRight = int(win.winfo_screenwidth() / 2.6 - windowWidth / 2)
        positionDown = int(win.winfo_screenheight() / 3.5 - windowHeight / 2)

        # Positions the window in the center of the page.
        win.geometry("+{}+{}".format(positionRight, positionDown))
    else:
        # Gets the requested values of the height and width.
        windowWidth = statusbox.winfo_reqwidth()
        windowHeight = statusbox.winfo_reqheight()

        # Gets both half the screen width/height and window width/height
        positionRight = int(statusbox.winfo_screenwidth() / 2.6 - windowWidth / 2)
        positionDown = int(statusbox.winfo_screenheight() / 3.5 - windowHeight / 2)

        # Positions the window in the center of the page.
        statusbox.geometry("+{}+{}".format(positionRight, positionDown))


def pop_up_init_(win):  # function to initialise test result popup children
    # button index map:
    # btn1_good or add_good = 1
    # btn1_bad or add_bad = 2
    # btn1_unclassified or add_unclassified = 3
    # btn2_good or add_good = 4
    # btn2_bad or add_bad = 5
    # btn2_unclassified or add_unclassified = 6
    # btn3_good or add_good = 7
    # btn3_bad or add_bad = 8
    # btn3_unclassified or add_unclassified = 9
    # btn4_good or add_good = 10
    # btn4_bad or add_bad = 11
    # btn4_unclassified or add_unclassified = 12
    # btn5_good or add_good = 13
    # btn5_bad or add_bad = 14
    # btn5_unclassified or add_unclassified = 15
    # get global references
    global txt1_test, btn1_addgood, btn1_addbad, txt2_test, btn2_addgood, btn2_addbad, txt3_test, btn3_addgood, \
        btn3_addbad, txt4_test, btn4_addgood, btn4_addbad, txt5_test, btn5_addgood, btn5_addbad, btn1_add_unclassified,\
        btn2_add_unclassified, btn3_add_unclassified, btn4_add_unclassified, btn5_add_unclassified

    # initialize test buttons
    txt1_test = Label(win, text="")
    btn1_addgood = Button(win, text="MARK AS SEATED", width=30, command=partial(copytofolder, "img1.jpg", 1, "goodFolder1", 1))
    btn1_addbad = Button(win, text="MARK AS UNSEATED", width=30, command=partial(copytofolder, "img1.jpg", 1, "badFolder1", 2))
    btn1_add_unclassified = Button(win, text="USELESS", width=30, command=partial(copytofolder, "img1.jpg", 1, "random_image", 3))
    # img2
    txt2_test = Label(win, text="")
    btn2_addgood = Button(win, text="MARK AS SEATED", width=30, command=partial(copytofolder, "img2.jpg", 1, "goodFolder2", 4))
    btn2_addbad = Button(win, text="MARK AS UNSEATED", width=30, command=partial(copytofolder, "img2.jpg", 1, "badFolder2", 5))
    btn2_add_unclassified = Button(win, text="USELESS", width=30, command=partial(copytofolder, "img2.jpg", 1, "random_image", 6))
    # img3
    txt3_test = Label(win, text="")
    btn3_addgood = Button(win, text="MARK AS SEATED", width=30, command=partial(copytofolder, "img3.jpg", 1, "goodFolder3", 7))
    btn3_addbad = Button(win, text="MARK AS UNSEATED", width=30, command=partial(copytofolder, "img3.jpg", 1, "badFolder3", 8))
    btn3_add_unclassified = Button(win, text="USELESS", width=30, command=partial(copytofolder, "img3.jpg", 1, "random_image", 9))
    # img4
    txt4_test = Label(win, text="")
    btn4_addgood = Button(win, text="MARK AS SEATED", width=30, command=partial(copytofolder, "img4.jpg", 1, "goodFolder4", 10))
    btn4_addbad = Button(win, text="MARK AS UNSEATED", width=30, command=partial(copytofolder, "img4.jpg", 1, "badFolder4", 11))
    btn4_add_unclassified = Button(win, text="USELESS", width=30, command=partial(copytofolder, "img4.jpg", 1, "random_image", 12))
    # img5
    txt5_test = Label(win, text="")
    btn5_addgood = Button(win, text="MARK AS SEATED", width=30, command=partial(copytofolder, "img5.jpg", 1, "goodFolder5", 13))
    btn5_addbad = Button(win, text="MARK AS UNSEATED", width=30, command=partial(copytofolder, "img5.jpg", 1, "badFolder5", 14))
    btn5_add_unclassified = Button(win, text="USELESS", width=30, command=partial(copytofolder, "img5.jpg", 1, "random_image", 15))


# function to show test result popup
def popup_test_result(textboxnum, textstr):
    win = Toplevel()
    win.wm_title("Results For Camera: " + str(textboxnum))
    testimage = cv2.imread(os.getcwd() + '/test_images/testIMG' + str(textboxnum) + ".jpg")  # read file
    scaleX, scaleY = rescaleimg(610, 400, testimage)  # get scaling proportions
    # OpenCV represents images in BGR order; however PIL represents
    # images in RGB order, so we need to swap the channels
    testimage = cv2.cvtColor(testimage, cv2.COLOR_BGR2RGB)
    # convert the images to PIL format...
    testimage = Image.fromarray(testimage)
    # resize image
    testimage = testimage.resize((scaleX, scaleY), Image.ANTIALIAS)
    # ...and then convert to ImageTk format
    testimage = ImageTk.PhotoImage(testimage)
    imgBox = Label(win, image=testimage)
    imgBox.Image = testimage
    imgBox.grid(row=0, column=0, rowspan=3, columnspan=2, padx=10, pady=10)
    pop_up_init_(win)
    updateResults(textboxnum, textstr)
    showresultfeatures(textboxnum)
    b = Button(win, text="EXIT", command=win.destroy)
    b.grid(row=6, columnspan=2, column=0, padx=10, pady=10, sticky=W + E + N + S)
    centerWindow(win, True)  # local variable


def loadPromptPopUp(text):  # function to show loading prompt
    global statusbox
    text = text.upper()  # capitalize
    statusbox = Toplevel(bd=10, relief=RIDGE)  # add border and shading
    statusbox.wm_title("")
    statusbox.overrideredirect(True)  # don't allow user close window
    txtBox = Label(statusbox, text=text, width=50)
    txtBox.grid(row=0, column=0, rowspan=3, columnspan=2, padx=10, pady=50)
    centerWindow(None, False)  # Feeding in global variable


def close_loadPromptPopUp():  # closes the text loading prompt window
    statusbox.destroy()


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
    Checkbutton(root, text=mylbl, variable=testmodeCtrl, command=show_hide_btns).grid(row=11, column=0, sticky=W, padx="10", pady="20")

    # close window event handler
    root.protocol("WM_DELETE_WINDOW", on_close)
    # kick off the GUI
    root.mainloop()


if __name__ == "__main__":  # define main function
    main()
