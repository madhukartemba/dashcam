import logging
import os
import cv2
from main import LOGS_FOLDER
import utils.utils as utils
from inference.labels import Label
from input_output.video_recovery import VideoRecovery
from input_output.input_source_process import InputSourceProcess
from inference.inference import Inference


# File config
RECOVERY_FOLDER = "recovery"
OUTPUT_FOLDER = "recordings"
FILE_DURATION = 120

# Logging
LOGS_FOLDER = "logs"
if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)
logging.basicConfig(
    filename=os.path.join(LOGS_FOLDER, "errors.log"),
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Input Source
FPS = 30.0
CAMERA_ID = 0
WIDTH = 1280
HEIGHT = 720
SHOW_PREVIEW = True

# Labels
RED = Label(0, "red")
GREEN = Label(1, "green")
YELLOW = Label(2, "yellow")
OFF = Label(3, "off")

# Inference
MODEL = "models/6thMar2024/traffic_6thMar2024.tflite"
SCORE_THRESHOLD = 0.55
MAX_RESULTS = 3
NUM_THREADS = 2

# Actions
ACTIONS_DICT = {
    (RED.index, GREEN.index): lambda: utils.playSound("sounds/green.mp3"),
    (YELLOW.index, GREEN.index): lambda: utils.playSound("sounds/green.mp3"),
    (RED.index, YELLOW.index): lambda: utils.playSound("sounds/yellow.mp3"),
    (GREEN.index, YELLOW.index): lambda: utils.playSound("sounds/yellow.mp3"),
    (None, YELLOW.index): lambda: utils.playSound("sounds/yellow.mp3"),
    (GREEN.index, RED.index): lambda: utils.playSound("sounds/red.mp3"),
    (YELLOW.index, RED.index): lambda: utils.playSound("sounds/red.mp3"),
    (None, RED.index): lambda: utils.playSound("sounds/red.mp3"),
}


if __name__ == "__main__":

    # Start recovery as soon as the program starts
    videoRecovery = VideoRecovery(RECOVERY_FOLDER, OUTPUT_FOLDER, FPS)
    videoRecovery.recoverVideo()

    # Open input source process with built-in dashcam recording
    inputSource = InputSourceProcess(
        CAMERA_ID, WIDTH, HEIGHT, OUTPUT_FOLDER, RECOVERY_FOLDER, FILE_DURATION, FPS
    )
    inputSource.start()

    # Start inference
    inference = Inference(
        inputSource,
        [GREEN.index, YELLOW.index, RED.index, OFF.index],
        MODEL,
        SCORE_THRESHOLD,
        MAX_RESULTS,
        NUM_THREADS,
        ACTIONS_DICT,
        maxFps=FPS,
        categoriesDeniedList=[OFF.name],
        showPreview=SHOW_PREVIEW,
    )

    try:
        while not inputSource.stopEvent.is_set():
            inference.infer()

            if SHOW_PREVIEW and cv2.waitKey(1) == ord("q"):
                break

    except KeyboardInterrupt:
        print("Closing the application...")
    except Exception as e:
        utils.playSound("sounds/error.mp3")
        print(e)
        logging.error(e)
    finally:
        inference.destroyWindow()
        inference.stop()
        inputSource.stop()

    pass
