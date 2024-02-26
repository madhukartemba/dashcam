import cv2
import time


class InputSource:
    def __init__(self, videoSource, width=None, height=None) -> None:
        self.videoSource = videoSource

        if str(videoSource).isdigit():
            sourceId = int(videoSource)
            self.capture = cv2.VideoCapture(sourceId)
            if width is None or height is None:
                raise Exception(
                    "You need to provide the dimensions when using a camera"
                )
            else:
                self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        else:
            self.capture = cv2.VideoCapture(videoSource)

        self.image = None
        self.frameCount = 0
        self.openCaptureCheck()
        self.frameCount = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = 0
        self.lastTime = time.time()

    def isCaptureOpen(self):
        return self.capture.isOpened()

    def openCaptureCheck(self):
        if self.isCaptureOpen() == False:
            raise Exception("Capture is not opened")
        pass

    def getImage(self):

        self.openCaptureCheck()

        success, image = self.capture.read()

        if success == False:
            raise Exception("Capture failed")

        self.image = image

        # Calculate FPS
        currentTime = time.time()
        elapsedTime = currentTime - self.lastTime
        self.fps = 1 / elapsedTime
        self.lastTime = currentTime

        return image

    def releaseCapture(self):
        self.capture.release()

    def getDimensions(self):
        return (self.width, self.height)

    def getFps(self):
        return self.fps


if __name__ == "__main__":
    videoInputSource = InputSource("videos/journey.mp4")
    print(videoInputSource.getDimensions(), videoInputSource.frameCount)
    videoInputSource.releaseCapture()

    cameraInputSource = InputSource(0, 1280, 720)
    print(cameraInputSource.getDimensions())
    cameraInputSource.releaseCapture()
