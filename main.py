import cv2
import utils.utils as utils
from inference.labels import Label
from input_output.video_recovery import VideoRecovery
from input_output.input_source import InputSource
from input_output.dashcam import Dashcam
from inference.inference import Inference


# File config
RECOVERY_FOLDER = "recovery"
OUTPUT_FOLDER = "recordings"
FILE_DURATION = 600

# Input Source
FPS = 30.0
CAMERA_ID = "videos/combinedOutput1.mp4"
WIDTH = 1280
HEIGHT = 720
SHOW_PREVIEW = True

# Labels
RED = Label(0, "red")
GREEN = Label(1, "green")
YELLOW = Label(2, "yellow")
OFF = Label(3, "off")

# Inference
MODEL = "models/3rdMar2024/traffic_3rdMar2024.tflite"
SCORE_THRESHOLD = 0.55
MAX_RESULTS = 3
NUM_THREADS = 2

# Actions
ACTIONS_DICT = {
    (RED.index, GREEN.index): lambda: utils.playSound("sounds/green.mp3"),
    (YELLOW.index, GREEN.index): lambda: utils.playSound("sounds/green.mp3"),
    (GREEN.index, YELLOW.index): lambda: utils.playSound("sounds/yellow.mp3"),
    (None, YELLOW.index): lambda: utils.playSound("sounds/yellow.mp3"),
    (GREEN.index, RED.index): lambda: utils.playSound("sounds/red.mp3"),
    (YELLOW.index, RED.index): lambda: utils.playSound("sounds/red.mp3"),
    (None, RED.index): lambda: utils.playSound("sounds/red.mp3"),
}


if __name__ == "__main__":

    utils.playSound("sounds/startup.mp3")

    # Start recovery as soon as the program starts
    videoRecovery = VideoRecovery(RECOVERY_FOLDER, OUTPUT_FOLDER, FPS)
    videoRecovery.recoverVideo()

    # Open input source
    inputSource = InputSource(CAMERA_ID, WIDTH, HEIGHT, FPS)
    inputSource.start()

    # Start up dashcam recording
    dashcam = Dashcam(inputSource, FILE_DURATION, OUTPUT_FOLDER, RECOVERY_FOLDER, FPS)
    dashcam.start()

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
        while True:
            inference.infer()

            if SHOW_PREVIEW and cv2.waitKey(1) == ord("q"):
                break

    except KeyboardInterrupt:
        print("Closing the application...")
    except Exception as e:
        utils.playSound("sounds/error.mp3")
        print(e)
    finally:
        inference.destroyWindow()
        inference.stop()
        dashcam.stop()
        inputSource.stop()

    pass
