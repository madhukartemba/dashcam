import cv2
import numpy as np
import pygame
import time
from tflite_support.task import processor

# Initialize pygame mixer
pygame.mixer.init()

_MARGIN = 10  # pixels
_ROW_SIZE = 10  # pixels
_FONT_SIZE = 1
_FONT_THICKNESS = 1
_TEXT_COLOR = (0, 255, 0)  # red


def playSound(source: str, wait=False):
    pygame.mixer.music.load(source)
    pygame.mixer.music.play()
    if wait:
        while pygame.mixer.music.get_busy():
            time.sleep(0.5)
            continue


def putText(
    image: np.ndarray,
    text,
    text_location,
    font_size=_FONT_SIZE,
    text_color=_TEXT_COLOR,
    font_thickness=_FONT_THICKNESS,
):
    cv2.putText(
        image,
        text,
        text_location,
        cv2.FONT_HERSHEY_PLAIN,
        font_size,
        text_color,
        font_thickness,
    )


def visualize(
    image: np.ndarray,
    detections: list[processor.Detection],
) -> np.ndarray:
    for detection in detections:
        # Draw bounding_box
        bbox = detection.bounding_box
        start_point = bbox.origin_x, bbox.origin_y
        end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
        cv2.rectangle(image, start_point, end_point, _TEXT_COLOR, 3)

        # Draw label and score
        category = detection.categories[0]
        category_name = category.category_name
        probability = round(category.score, 2)
        result_text = category_name + " (" + str(probability) + ")"
        text_location = (_MARGIN + bbox.origin_x, _MARGIN + _ROW_SIZE + bbox.origin_y)
        cv2.putText(
            image,
            result_text,
            text_location,
            cv2.FONT_HERSHEY_PLAIN,
            _FONT_SIZE,
            _TEXT_COLOR,
            _FONT_THICKNESS,
        )

    return image


def getCategory(detection: processor.Detection):
    return detection.categories[0]

def getCategoryName(detection: processor.Detection):
    return detection.categories[0].display_name
