import time
import os
import threading
from input_source import InputSource
from process_input_source import ProcessInputSource
from video_recorder import VideoRecorder


class Dashcam:
    def __init__(
        self,
        inputSource: InputSource | ProcessInputSource,
        fileDuration=600,
        outputFolder="recordings",
        recoveryFolder="recovery",
        fps=30.0,
    ):
        self.fileDuration = fileDuration
        self.inputSource = inputSource

        if not os.path.exists(outputFolder):
            os.makedirs(outputFolder)

        self.outputFolder = outputFolder
        self.recoveryFolder = recoveryFolder
        self.fps = fps
        self.thread = None
        self.stopEvent = threading.Event()
        pass

    def record(self):
        while not self.stopEvent.is_set():
            fileName = f"{int(time.time())}.mp4"
            outputFile = os.path.join(self.outputFolder, fileName)
            videoRecorder = VideoRecorder(
                self.inputSource, outputFile, self.fps, self.recoveryFolder
            )
            videoRecorder.start()

            startTime = time.time()

            while (
                time.time() - startTime
            ) < self.fileDuration and not self.stopEvent.is_set():
                time.sleep(1)

            videoRecorder.stop()

    def start(self):
        self.thread = threading.Thread(target=self.record)
        self.thread.start()

    def stop(self):
        self.stopEvent.set()
        if self.thread:
            self.thread.join()


if __name__ == "__main__":

    inputSource = InputSource(0, 1280, 720)

    inputSource.start()

    dashcam = Dashcam(inputSource, fileDuration=5)
    dashcam.start()

    time.sleep(25)

    dashcam.stop()

    inputSource.stop()
