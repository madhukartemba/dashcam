import logging
import cv2
import time
import threading
import utils.utils as utils


class InputSource:
    def __init__(self, videoSource, width=None, height=None, maxFps=30.0) -> None:
        self.videoSource = videoSource

        self.thread = None
        self.stopEvent = threading.Event()
        self.startedEvent = threading.Event()

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

        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.image = None
        self.frameCount = 0
        self.openCaptureCheck()
        self.frameCount = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = 0
        self.maxFps = maxFps
        self.lastTime = time.time()

    def isCaptureOpen(self):
        return self.capture.isOpened()

    def openCaptureCheck(self):
        if self.isCaptureOpen() == False:
            raise Exception("Capture is not opened")
        pass

    def start(self):
        self.thread = threading.Thread(target=self.captureFrames)
        self.thread.start()
        self.startedEvent.wait(timeout=10)

    def stop(self):
        self.stopEvent.set()
        if self.thread:
            self.thread.join()

    def captureFrames(self):
        try:
            self.refreshFrame()
            self.startedEvent.set()
            frameInterval = 1 / self.maxFps
            while (not self.stopEvent.is_set()) and self.isCaptureOpen():
                startTime = time.time()
                self.refreshFrame()
                endTime = time.time()
                elapsedTime = endTime - startTime
                waitTime = max(0, frameInterval - elapsedTime)
                time.sleep(waitTime)
        except Exception as e:
            utils.playSound("sounds/error.mp3")
            print(e)
            logging.error(e)
        finally:
            self.stopEvent.set()
            self.releaseCapture()

    def refreshFrame(self):

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

    def getImage(self):
        return self.image

    def releaseCapture(self):
        self.capture.release()

    def getDimensions(self):
        return (self.width, self.height)

    def getFps(self):
        return self.fps


if __name__ == "__main__":
    videoInputSource = InputSource("videos/journey.mp4")
    print(videoInputSource.getDimensions(), videoInputSource.frameCount)
    videoInputSource.start()
    try:
        while True:
            image = videoInputSource.getImage()
            if image is not None:
                fps_text = "FPS = {:.1f}".format(videoInputSource.getFps())
                utils.putText(image, fps_text, (24, 20))
                cv2.imshow("Video", image)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        videoInputSource.stop()
        videoInputSource.releaseCapture()
        cv2.destroyAllWindows()

    cameraInputSource = InputSource(0, 1280, 720)
    print(cameraInputSource.getDimensions())
    cameraInputSource.start()
    try:
        while True:
            image = cameraInputSource.getImage()
            if image is not None:
                fps_text = "FPS = {:.1f}".format(cameraInputSource.getFps())
                utils.putText(image, fps_text, (24, 20))
                cv2.imshow("Camera", image)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        cameraInputSource.stop()
        cameraInputSource.releaseCapture()
        cv2.destroyAllWindows()
