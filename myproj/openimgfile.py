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
import tensorflow as tf
import numpy as np

# module-level variables ##############################################################################################
RETRAINED_LABELS_TXT_FILE_LOC = os.getcwd() + "/" + "retrained_labels.txt"
RETRAINED_GRAPH_PB_FILE_LOC = os.getcwd() + "/" + "retrained_graph.pb"

TEST_IMAGES_DIR = os.getcwd() + "/test_images"

SCALAR_RED = (0.0, 0.0, 255.0)
SCALAR_BLUE = (255.0, 0.0, 0.0)
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


def getresult(myimgpath, num, textboxnum, testimgname):
    hidetestbtns()  # don't allow any buttons to show while test is running
    copytofolder(myimgpath, num, testimgname)
    if not checkIfNecessaryPathsAndFilesExist():
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
                # if the classification (obtained from the directory name) ends with the letter "s", remove the "s" to change from plural to singular
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
    # write the graph to file so we can view with TensorBoard
    tfFileWriter = tf.summary.FileWriter(os.getcwd())
    tfFileWriter.add_graph(sess.graph)
    tfFileWriter.close()
    showresultfeatures()  # show result variables
    showtestbtns()  # show the buttons again
    updateResults(textboxnum, textstr)
# end main


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

def clearResults():
    # get global references
    global txt1_test, txt2_test, txt3_test, txt4_test, txt5_test
    txt1_test["text"] = ""
    txt2_test["text"] = ""
    txt3_test["text"] = ""
    txt4_test["text"] = ""
    txt5_test["text"] = ""


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


def copytofolder(myimgpath, num, folderpath):
    # num = 1 ===> training path, anything else => testing path
    myimgpath = os.getcwd() + "/" + myimgpath
    if num == 1: # append file
        # path to folders of image, timestamp added to give image a distinct name
        folderpath = os.getcwd() + '/training_images/' + folderpath + '/image' + str(time.time()) + ".jpg"
        os.makedirs(os.path.dirname(folderpath), exist_ok=True)  # create directory if it doesn't exist
        os.rename(myimgpath, folderpath)
    else:
        # for training, use folderpath as image name straight, overwrite
        folderpath = os.getcwd() + '/test_images/' + folderpath + ".jpg"
        shutil.copy(myimgpath, folderpath)


def classificationbtn_init_():
    # get global references
    global btn1_bad, btn1_good, btn2_bad, btn2_good, btn3_bad, btn3_good, btn4_bad, btn4_good, btn5_bad, btn5_good, \
        panelA, panelB, panelC, panelD, panelE
    # initialize classification buttons
    # WE USE THE "PARTIAL" KEYWORD TO PASS IN ARGS WITH A FUNCTION WHEN ONLY FUNCTION NAME IS EXPECTED
    btn1_good = Button(root, text="GOOD", width=30, command=partial(copytofolder, "img1.jpg", 1, "goodFolder1"))
    btn1_bad = Button(root, text="BAD", width=30, command=partial(copytofolder, "img1.jpg", 1, "badFolder1"))
    # img2
    btn2_good = Button(root, text="GOOD", width=30, command=partial(copytofolder, "img2.jpg", 1, "goodFolder2"))
    btn2_bad = Button(root, text="BAD", width=30, command=partial(copytofolder, "img2.jpg", 1, "badFolder2"))
    # img3
    btn3_good = Button(root, text="GOOD", width=30, command=partial(copytofolder, "img3.jpg", 1, "goodFolder3"))
    btn3_bad = Button(root, text="BAD", width=30, command=partial(copytofolder, "img3.jpg", 1, "badFolder3"))
    # img4
    btn4_good = Button(root, text="GOOD", width=30, command=partial(copytofolder, "img4.jpg", 1, "goodFolder4"))
    btn4_bad = Button(root, text="BAD", width=30, command=partial(copytofolder, "img4.jpg", 1, "badFolder4"))
    # img5
    btn5_good = Button(root, text="GOOD", width=30, command=partial(copytofolder, "img5.jpg", 1, "goodFolder5"))
    btn5_bad = Button(root, text="BAD", width=30, command=partial(copytofolder, "img5.jpg", 1, "badFolder5"))


def testbtn_init_():
    # get global references
    global btn1_test, txt1_test, btn1_addgood, btn1_addbad, btn2_test, txt2_test, btn2_addgood, btn2_addbad, btn3_test,\
        txt3_test, btn3_addgood, btn3_addbad, btn4_test, txt4_test, btn4_addgood, btn4_addbad, btn5_test, txt5_test,\
        btn5_addgood, btn5_addbad

    # initialize test buttons
    btn1_test = Button(root, text="TEST", width=30, command=partial(getresult, "img1.jpg", 0, 1, "testIMG1"))
    txt1_test = Label(root, text="")
    btn1_addgood = Button(root, text="ADD TO GOOD", width=30, command="")
    btn1_addbad = Button(root, text="ADD TO BAD", width=30, command="")
    # img2
    btn2_test = Button(root, text="TEST", width=30, command=partial(getresult, "img2.jpg", 0, 2, "testIMG2"))
    txt2_test = Label(root, text="")
    btn2_addgood = Button(root, text="ADD TO GOOD", width=30, command="")
    btn2_addbad = Button(root, text="ADD TO BAD", width=30, command="")
    # img3
    btn3_test = Button(root, text="TEST", width=30, command=partial(getresult, "img3.jpg", 0, 3, "testIMG3"))
    txt3_test = Label(root, text="")
    btn3_addgood = Button(root, text="ADD TO GOOD", width=30, command="")
    btn3_addbad = Button(root, text="ADD TO BAD", width=30, command="")
    # img4
    btn4_test = Button(root, text="TEST", width=30, command=partial(getresult, "img4.jpg", 0, 4, "testIMG4"))
    txt4_test = Label(root, text="")
    btn4_addgood = Button(root, text="ADD TO GOOD", width=30, command="")
    btn4_addbad = Button(root, text="ADD TO BAD", width=30, command="")
    # img5
    btn5_test = Button(root, text="TEST", width=30, command=partial(getresult, "img5.jpg", 0, 5, "testIMG5"))
    txt5_test = Label(root, text="")
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
    btn1_test.grid(row=3, column=0, padx="10", pady="10", sticky=W)
    btn2_test.grid(row=3, column=3, padx="10", pady="10", sticky=W)
    btn3_test.grid(row=3, column=6, padx="10", pady="10", sticky=W)
    btn4_test.grid(row=8, column=0, padx="10", pady="10", sticky=W)
    btn5_test.grid(row=8, column=3, padx="10", pady="10", sticky=W)


def showresultfeatures():
    # get global references
    global txt1_test, btn1_addgood, btn1_addbad, txt2_test, btn2_addgood, btn2_addbad, txt3_test, btn3_addgood,\
        btn3_addbad, txt4_test, btn4_addgood, btn4_addbad, txt5_test, btn5_addgood, btn5_addbad
    # textboxes
    txt1_test.grid(row=4, column=0, padx="10", pady="10", sticky=W)
    txt2_test.grid(row=4, column=3, padx="10", pady="10", sticky=W)
    txt3_test.grid(row=4, column=6, padx="10", pady="10", sticky=W)
    txt4_test.grid(row=9, column=0, padx="10", pady="10", sticky=W)
    txt5_test.grid(row=9, column=3, padx="10", pady="10", sticky=W)
    # buttons
    btn1_addgood.grid(row=3, column=1, padx="10", pady="10", sticky=W)
    btn2_addgood.grid(row=3, column=4, padx="10", pady="10", sticky=W)
    btn3_addgood.grid(row=3, column=7, padx="10", pady="10", sticky=W)
    btn4_addgood.grid(row=8, column=1, padx="10", pady="10", sticky=W)
    btn5_addgood.grid(row=8, column=4, padx="10", pady="10", sticky=W)
    btn1_addbad.grid(row=4, column=1, padx="10", pady="10", sticky=W)
    btn2_addbad.grid(row=4, column=4, padx="10", pady="10", sticky=W)
    btn3_addbad.grid(row=4, column=7, padx="10", pady="10", sticky=W)
    btn4_addbad.grid(row=9, column=1, padx="10", pady="10", sticky=W)
    btn5_addbad.grid(row=9, column=4, padx="10", pady="10", sticky=W)


def hidetestbtns():
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
    Checkbutton(root, text=mylbl, variable=testmodeCtrl, command=show_hide_btns).grid(row=10, column=0, sticky=W, padx="10", pady="20")

    # kick off the GUI
    root.mainloop()


if __name__ == "__main__":  # define main function
    main()
