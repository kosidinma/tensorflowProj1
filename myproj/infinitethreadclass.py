# import the necessary packages
from threading import Thread  # we're using threads

# infinite thread class
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


def myloopFunction():
    print("lol")


def main():
    # start timer
    t = InfiniteLoop(myloopFunction)  # every 0.1s
    t.start()


if __name__ == "__main__":  # define main function
    main()
