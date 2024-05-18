import logging
import threading
import time
import cv2
import numpy as np
from api_server import APIData, LightMode
from input_output.input_source import InputSource

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


class LightDetection:
    def __init__(
        self,
        inputSource: InputSource,
        apiData: APIData,
        thresholdBrightnessDark=75,
        thresholdBrightnessLight=120,
    ):
        self.thread = None
        self.inputSource = inputSource
        self.stopEvent = threading.Event()
        self.thresholdBrightnessDark = thresholdBrightnessDark
        self.thresholdBrightnessLight = thresholdBrightnessLight
        self.lightMode = LightMode.DARK.value
        self.apiData = apiData
        pass

    def detect(self):
        try:
            while not self.stopEvent.is_set():
                image = self.inputSource.getImage()
                grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                averageBrightness = np.mean(grayImage)
                if (
                    self.lightMode == LightMode.DARK.value
                    and averageBrightness > self.thresholdBrightnessLight
                ):
                    self.lightMode = LightMode.BRIGHT.value
                elif (
                    self.lightMode == LightMode.BRIGHT.value
                    and averageBrightness < self.thresholdBrightnessDark
                ):
                    self.lightMode = LightMode.DARK.value
                self.apiData.lightMode = self.lightMode
                time.sleep(1)
        except Exception as e:
            print(e)
            logging.error(e)
            self.apiData.lightMode = LightMode.DARK.value
            self.stopEvent.set()

    def start(self):
        self.thread = threading.Thread(target=self.detect)
        self.thread.start()

    def stop(self):
        self.stopEvent.set()
        if self.thread:
            self.thread.join()
