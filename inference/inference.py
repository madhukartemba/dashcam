import time
import cv2
from main import APIData
import utils.utils as utils
import threading
import logging
from input_output.input_source import InputSource
from input_output.input_source_process import InputSourceProcess
from inference.inference_engine import InferenceEngine
from inference.detection_filter import DetectionFilter
from inference.final_decision import FinalDecision
from inference.actions import Actions


class Inference:
    def __init__(
        self,
        inputSource,
        indexPriority,
        model,
        scoreThreshold,
        maxResults,
        numThreads,
        actionsDict,
        maxFps,
        apiData: APIData,
        categoriesDeniedList=None,
        showPreview=True,
    ) -> None:

        self.thread = None
        self.stopEvent = threading.Event()

        self.inputSource = inputSource
        self.showPreview = showPreview

        self.inferenceEngine = InferenceEngine(
            model, categoriesDeniedList, numThreads, scoreThreshold, maxResults
        )

        self.detectionFilter = DetectionFilter(
            inputSource.width, inputSource.height, maxAreaDivisor=16
        )

        self.finalDecision = FinalDecision(indexPriority)

        self.actions = Actions(actionsDict)

        self.fpsLastTime = time.time()

        self.frameInterval = 1 / maxFps

        self.fps = 0

        self.apiData = apiData

        pass

    def run(self):
        while not self.stopEvent.is_set():
            self.infer()

        self.destroyWindow()
        pass

    def infer(self):
        startTime = time.time()
        if isinstance(self.inputSource, InputSourceProcess):
            image = self.inputSource.requestImage()
        else:
            image = self.inputSource.getImage()

        self.finalDecision.updateMinCount(int(self.fps))
        self.actions.updateBufferSize(int(10 * self.fps))

        detectionResult = self.inferenceEngine.getDetections(image)

        detections = self.detectionFilter.filter(detectionResult)

        detection = self.finalDecision.getDecision(detections)
        if self.apiData:
            self.apiData.trafficLightColor = utils.getCategory(detection).display_name
            self.apiData.fps = self.fps

        self.actions.act(
            index=(
                utils.getCategory(detection).index if detection is not None else None
            )
        )

        if self.showPreview:
            fps_text = "FPS = {:.1f}".format(self.fps)
            utils.putText(image, fps_text, (24, 20))

            if detection != None:
                image = utils.visualize(image, [detection])

            cv2.imshow("Inference", image)
            cv2.waitKey(1)

        currentTime = time.time()
        elapsedTime = currentTime - startTime
        time.sleep(max(0, self.frameInterval - elapsedTime))
        self.fps = 1 / (time.time() - startTime)
        pass

    def destroyWindow(self):
        try:
            if self.showPreview:
                cv2.destroyWindow("Inference")
        except Exception as e:
            utils.playSound("sounds/error.mp3")
            print(e)
            logging.error(e)

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self):
        self.stopEvent.set()
        if self.thread:
            self.thread.join()
