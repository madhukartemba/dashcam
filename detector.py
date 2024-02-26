from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision


import cv2
import numpy as np


class Detector:
    def __init__(self, model, threads=2, score_threshold=0.5, max_results=3) -> None:
        base_options = core.BaseOptions(
            file_name=model, use_coral=False, num_threads=threads
        )
        detection_options = processor.DetectionOptions(
            max_results=max_results, score_threshold=score_threshold
        )
        options = vision.ObjectDetectorOptions(
            base_options=base_options, detection_options=detection_options
        )
        self.model = model
        self.detector = vision.ObjectDetector.create_from_options(options)
        pass

    def getDetections(self, image: np.ndarray):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        input_tensor = vision.TensorImage.create_from_array(rgb_image)
        return self.detector.detect(input_tensor)
