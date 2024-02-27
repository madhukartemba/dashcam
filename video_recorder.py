import threading
import time
import os
import cv2
import shutil
from input_source import InputSource
from video_maker import VideoMaker


class VideoRecorder:
    def __init__(
        self,
        inputSource: InputSource,
        outputFile: str,
        fps: float = 30.0,
        recoveryFolder: str = "recovery",
    ) -> None:
        self.inputSource = inputSource
        self.outputFile = outputFile
        self.fps = fps
        self.recoveryFolder = recoveryFolder
        self.videoMaker = VideoMaker(
            outputFile, inputSource.width, inputSource.height, self.fps
        )

        self.mainThread = None
        self.recoveryThread = None
        self.stopEvent = threading.Event()
        pass

    def recordVideo(self):
        frameInterval = 1 / self.fps
        while not self.stopEvent.is_set():
            startTime = time.time()

            image = self.inputSource.getImage()

            if image is None:
                continue

            self.videoMaker.writeFrame(image)

            endTime = time.time()
            elapsedTime = endTime - startTime
            waitTime = max(0, frameInterval - elapsedTime)
            time.sleep(waitTime)

    def recovery(self):
        if not os.path.exists(self.recoveryFolder):
            os.makedirs(self.recoveryFolder)
        frameInterval = 1 / self.fps
        frameCount = 0
        while not self.stopEvent.is_set():
            startTime = time.time()

            image = self.inputSource.getImage()

            if image is None:
                continue

            frameCount += 1
            cv2.imwrite(f"{self.recoveryFolder}/{frameCount}.jpg", image)
            endTime = time.time()
            elapsedTime = endTime - startTime
            waitTime = max(0, frameInterval - elapsedTime)
            time.sleep(waitTime)

    def start(self):
        self.mainThread = threading.Thread(target=self.recordVideo)
        self.mainThread.start()
        self.recoveryThread = threading.Thread(target=self.recovery)
        self.recoveryThread.start()

    def stop(self):
        self.stopEvent.set()
        if self.mainThread:
            self.mainThread.join()
        if self.recoveryThread:
            self.recoveryThread.join()
        self.videoMaker.releaseVideo()
        shutil.rmtree(self.recoveryFolder, ignore_errors=True)


if __name__ == "__main__":
    inputSource = InputSource(0, 1280, 720)
    # inputSource = InputSource("videos/journey.mp4")

    inputSource.start()

    outputFilePath = "outputs/output_video_test.mp4"
    fps = 30.0

    videoRecorder = VideoRecorder(inputSource, outputFilePath, fps)
    videoRecorder.start()
    time.sleep(5)
    videoRecorder.stop()
    inputSource.stop()
