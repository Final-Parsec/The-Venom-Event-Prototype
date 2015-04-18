from threading import Thread
from time import sleep


class RepeatTask(Thread):
    def __init__(self, interval, function, *args, **kwargs):
        Thread.__init__(self)

        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.runnable = True

    def run(self):
        while self.runnable:
            try:
                self.function(*self.args, **self.kwargs)
            except Exception as error:
                print error
                print 'Function that threw exception: ' + str(self.function)
                print ('RepeatTask function threw unhandled exception. Thread is being stopped.')
                self.runnable = False
            sleep(self.interval)

    def stop(self):
        self.runnable = False