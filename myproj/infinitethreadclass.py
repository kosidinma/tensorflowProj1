# import the necessary packages
from threading import Thread  # we're using threads

# infinite thread class
class InfiniteLoop(Thread):
    def __init__(self, target, width):  # initialise variables and class input arguments
        Thread.__init__(self)
        self.running = True
        self.target = target
        self.width = width

    def run(self):
        while self.running:
            self.target(self.width)

    def stop(self):
        self.running = False


def myloopFunction(width):
    print("lol" + str(width))


def main():
    # start timer
    t = InfiniteLoop(myloopFunction, 1)  # every 0.1s
    t.start()


if __name__ == "__main__":  # define main function
    main()
