import multiprocessing
import cv2
import time
from dashcam import Dashcam

class ProcessInputSource:
    def __init__(self, videoSource, width, height, outputFolder, recoveryFolder, fileDuration=600, maxFps=30.0) -> None:
        self.videoSource = videoSource
        self.width = width
        self.height = height
        self.maxFps = maxFps
        self.fileDuration = fileDuration
        self.outputFolder = outputFolder
        self.recoveryFolder = recoveryFolder
        self.frame = None

        self.process = None
        self.stopEvent = multiprocessing.Event()
        self.stoppedEvent = multiprocessing.Event()
        self.startedEvent = multiprocessing.Event()
        self.frameRequestEvent = multiprocessing.Event()
        self.frameReadyEvent = multiprocessing.Event()
        self.imageQueue = multiprocessing.Queue(1)
        self.fps = multiprocessing.Value('d', 0.0)
    
    def start(self):
        print('Starting capture...')
        self.process = multiprocessing.Process(target=self.captureFrames)
        self.process.start()
        self.startedEvent.wait()
        time.sleep(3)
        print('Capture started')

    def stop(self):
        print('Stop capture is called...')
        self.stopEvent.set()
        print('Waiting for capture to stop...')
        self.stoppedEvent.wait()
        print('Capture stopped event received, terminating process...')
        self.process.terminate()
        print('Process terminated')

    def getVideoCapture(self):
        if str(self.videoSource).isdigit():
            sourceId = int(self.videoSource)
            capture = cv2.VideoCapture(sourceId)
            if self.width is None or self.height is None:
                raise Exception("You need to provide dimensions when using a camera")
            else:
                capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            return capture
        else:
            capture = cv2.VideoCapture(self.videoSource)
            self.width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return capture
    
    def captureFrames(self):
        frameInterval = 1/self.maxFps

        capture = self.getVideoCapture()
        self.startedEvent.set()
        startTime = time.time()
        fpsLastTime = time.time()

        dashcam = Dashcam(self, self.fileDuration, self.outputFolder, self.recoveryFolder, self.maxFps)
        dashcam.start()

        while (not self.stopEvent.is_set()) and capture.isOpened():
            succces, frame = capture.read()
            if not succces:
                raise Exception("Failed to capture frame")
            
            if self.frameRequestEvent.is_set():
                while not self.imageQueue.empty():
                    self.imageQueue.get()
                
                self.imageQueue.put(frame)
                self.frameRequestEvent.clear()
                self.frameReadyEvent.set()

            fps = (1/ (time.time() - fpsLastTime))
            fpsLastTime = time.time()
            self.fps.value = fps
            
            endTime = time.time()
            elapsedTime = endTime - startTime
            waitTime = max(0, frameInterval - elapsedTime)
            startTime = time.time()
            time.sleep(waitTime)
        
        dashcam.stop()
        capture.release()
        self.stoppedEvent.set()

    # Directly get the image, will only work in the same process
    def getImage(self):
        return self.frame
    
    # Request the image from the process
    def requestImage(self):
        self.frameRequestEvent.set()
        self.frameReadyEvent.wait()
        image = self.imageQueue.get()
        self.frameReadyEvent.clear()
        return image
    
    def getFps(self):
        return self.fps.value
    

if __name__ == "__main__":
    cameraInputSource = ProcessInputSource(0, 1280, 720)
    cameraInputSource.start()
    fps = 0
    fpsLastTime = time.time()
    try:
        while True:
            image = cameraInputSource.getImage()
            if image is not None:
                cv2.imshow("Camera", image)
                fps = (1/ (time.time() - fpsLastTime))
                fpsLastTime = time.time()
                print('Main thread FPS:', fps)
                print('Process FPS:', cameraInputSource.getFps())

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        cameraInputSource.stop()
        cv2.destroyAllWindows()