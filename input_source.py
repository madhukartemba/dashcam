import cv2


class InputSource:
    def __init__(self, videoSource, width=None, height=None) -> None:
        self.videoSource = videoSource
        try:
            sourceId = int(videoSource)
            self.capture = cv2.VideoCapture(sourceId)
        except:
            self.capture = cv2.VideoCapture(videoSource)
        self.image = None
        self.frameCount = 0
        if width is not None and height is not None:
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.openCaptureCheck()
        self.frameCount = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

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
        return image

    def releaseCapture(self):
        self.capture.release()

    def getDimensions(self):
        return (self.width, self.height)


if __name__ == "__main__":
    inputSource = InputSource(1280, 720)
    print(inputSource.width, inputSource.height)
    inputSource.releaseCapture()
