import argparse
import cv2
import utils
import threading
from typing import Dict, Tuple, Callable
from input_source import InputSource
from video_maker import VideoMaker
from inference_engine import InferenceEngine
from detection_filter import DetectionFilter
from final_decision import FinalDecision
from actions import Actions
from labels import Labels, Label


class Inference:
    def __init__(
        self,
        inputSource,
        showPreview,
        indexPriority,
        model,
        scoreThreshold,
        numThreads,
        actionsDict,
    ) -> None:

        self.thread = None
        self.stopEvent = threading.Event()

        self.inputSource = inputSource
        self.showPreview = showPreview

        self.inferenceEngine = InferenceEngine(model, numThreads, scoreThreshold)

        self.detectionFilter = DetectionFilter(
            inputSource.width, inputSource.height, maxAreaDivisor=16
        )

        self.finalDecision = FinalDecision(indexPriority)

        self.actions = Actions(actionsDict)

        pass
