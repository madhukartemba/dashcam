import time
import cv2
import utils
import threading
from input_output.input_source import InputSource
from input_output.input_source_process import InputSourceProcess
from inference.inference_engine import InferenceEngine
from inference.detection_filter import DetectionFilter
from inference.final_decision import FinalDecision
from actions import Actions


class Inference:
    def __init__(
        self,
        inputSource: InputSource | InputSourceProcess,
        indexPriority,
        model,
        scoreThreshold,
        maxResults,
        numThreads,
        actionsDict,
        showPreview=True,
    ) -> None:

        self.thread = None
        self.stopEvent = threading.Event()

        self.inputSource = inputSource
        self.showPreview = showPreview

        self.inferenceEngine = InferenceEngine(
            model, numThreads, scoreThreshold, maxResults
        )

        self.detectionFilter = DetectionFilter(
            inputSource.width, inputSource.height, maxAreaDivisor=16
        )

        self.finalDecision = FinalDecision(indexPriority)

        self.actions = Actions(actionsDict)

        self.fpsLastTime = time.time()

        pass

    def run(self):
        while not self.stopEvent.is_set():
            self.infer()

        self.destroyWindow()
        pass

    def infer(self):
        if isinstance(self.inputSource, InputSourceProcess):
            image = self.inputSource.requestImage()
        else:
            image = self.inputSource.getImage()
    
        currentTime = time.time()
        fps = 1 / (currentTime - self.fpsLastTime)
        self.fpsLastTime = currentTime

        self.finalDecision.updateMinCount(int(fps * 2 / 3))
        self.actions.updateBufferSize(10 * fps)

        detectionResult = self.inferenceEngine.getDetections(image)

        detections = self.detectionFilter.filter(detectionResult)

        detection = self.finalDecision.getDecision(detections)

        self.actions.act(
            index=(
                utils.getCategory(detection).index if detection is not None else None
            )
        )

        if self.showPreview:
            fps_text = "FPS = {:.1f}".format(fps)
            utils.putText(image, fps_text, (24, 20))

            if detection != None:
                image = utils.visualize(image, [detection])

            cv2.imshow("Inference", image)
            cv2.waitKey(1)

    def destroyWindow(self):
        if self.showPreview:
            cv2.destroyWindow("Inference")

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self):
        self.stopEvent.set()
        if self.thread:
            self.thread.join()