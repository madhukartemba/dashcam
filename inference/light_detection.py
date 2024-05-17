import logging
import threading
import cv2
import numpy as np
from api_server import APIData
from input_output.input_source import InputSource

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


class LightDetection:
    def __init__(
        self, inputSource: InputSource, apiData: APIData, thresholdBrightness=50
    ):
        self.thread = None
        self.inputSource = inputSource
        self.stopEvent = threading.Event()
        self.darkMode = True
        self.thresholdBrightness = thresholdBrightness
        self.apiData = apiData
        pass

    def detect(self):
        try:
            while not self.stopEvent.is_set():
                image = self.inputSource.getImage()
                grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                averageBrightness = np.mean(grayImage)
                self.darkMode = averageBrightness < self.thresholdBrightness
                self.apiData.darkMode = self.darkMode
        except Exception as e:
            print(e)
            logging.error(e)
            self.stopEvent.set()

    def start(self):
        self.thread = threading.Thread(target=self.detect)
        self.thread.start()

    def stop(self):
        self.stopEvent.set()
        if self.thread:
            self.thread.join()
