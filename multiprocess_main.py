import utils.utils as utils
from inference.labels import Label
from input_output.video_recovery import VideoRecovery
from input_output.input_source_process import InputSourceProcess
from inference.inference import Inference


# File config
RECOVERY_FOLDER = "recovery"
OUTPUT_FOLDER = "recordings"
FILE_DURATION = 600

# Input Source
FPS = 30.0
CAMERA_ID = 0
WIDTH = 1280
HEIGHT = 720

# Labels
RED = Label(0, "red")
GREEN = Label(1, "green")
YELLOW = Label(2, "yellow")
OFF = Label(3, "off")

# Inference
MODEL = "models/3rdMar2024/traffic_3rdMar2024.tflite"
SCORE_THRESHOLD = 0.4
MAX_RESULTS = 3
NUM_THREADS = 2

# Actions
ACTIONS_DICT = {
    (RED.index, GREEN.index): lambda: utils.playSound("sounds/key24.mp3"),
    (YELLOW.index, GREEN.index): lambda: utils.playSound("sounds/key24.mp3"),
    (GREEN.index, YELLOW.index): lambda: utils.playSound("sounds/key21.mp3"),
    (None, YELLOW.index): lambda: utils.playSound("sounds/key21.mp3"),
    (GREEN.index, RED.index): lambda: utils.playSound("sounds/key18.mp3"),
    (YELLOW.index, RED.index): lambda: utils.playSound("sounds/key18.mp3"),
    (None, RED.index): lambda: utils.playSound("sounds/key18.mp3"),
}


if __name__ == "__main__":
    try:
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
            showPreview=True,
        )

        while True:
            inference.infer()

    except Exception as e:
        print(e)
    finally:
        inference.destroyWindow()
        inference.stop()
        inputSource.stop()

    pass
