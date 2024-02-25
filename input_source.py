import cv2


class InputSource:
    def __init__(self, videoSource=0) -> None:
        self.videoSource = videoSource
        self.capture = cv2.VideoCapture(videoSource)
        self.image = None
        self.openCaptureCheck()
        self.width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        pass

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


if __name__ == "__main__":
    inputSource = InputSource("videos/journey.mp4")
    print(inputSource.width, inputSource.height)
