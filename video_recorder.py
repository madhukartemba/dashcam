import threading
import time
from input_source import InputSource
from video_maker import VideoMaker


class VideoRecorder:
    def __init__(
        self, inputSource: InputSource, outputFile: str, fps: float = 30.0
    ) -> None:
        self.inputSource = inputSource
        self.outputFile = outputFile
        self.fps = fps
        self.videoMaker = VideoMaker(
            outputFile, inputSource.width, inputSource.height, self.fps
        )

        self.thread = None
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

    def start(self):
        self.thread = threading.Thread(target=self.recordVideo)
        self.thread.start()

    def stop(self):
        self.stopEvent.set()
        if self.thread:
            self.thread.join()
        self.videoMaker.releaseVideo()


if __name__ == "__main__":
    inputSource = InputSource(0, 1280, 720)

    inputSource.run()

    outputFilePath = "outputs/output_video_test.mp4"
    fps = 30.0

    videoRecorder = VideoRecorder(inputSource, outputFilePath, fps)
    videoRecorder.start()
    time.sleep(5)
    videoRecorder.stop()
    inputSource.stop()
