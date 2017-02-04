from threading import Thread
from SetupUtil import *

import cv2


class MultithreadVideoStream:
    def __init__(self, src=0):
        '''Initialize and read camera stream'''
        setUpCamera(src)
        self.stream = cv2.VideoCapture(src)

        (self.grabbed, self.frame) = self.stream.read()

        '''Used to indicate if thread should be stopped'''
        self.stopped = False

    def start(self):
        '''Starts thread to read frame'''
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        '''Keep looping until thread is stopped'''
        while True:
            '''If thread should be stopped then stop'''
            if self.stopped:
                return

            '''Else just keep grabbing frames'''
            self.grabbed, self.frame = self.stream.read()

    def read(self):
        '''Return most recent frame'''
        return self.frame

    def release(self):
        self.stream.release()
        self.stopped = True

    def isOpened(self):
        return self.isOpened()
