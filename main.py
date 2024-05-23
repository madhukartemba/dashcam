from enum import Enum
import time
import cv2
import argparse
import logging
import os
from inference.light_detection import LightDetection
import utils.utils as utils
from api_server import APIServer, Status
from cleanup.cleanup import Cleanup
from inference.labels import Label
from input_output.video_recovery import VideoRecovery
from input_output.input_source import InputSource
from input_output.dashcam import Dashcam
from inference.inference import Inference


# File config
RECOVERY_FOLDER = "recovery"
OUTPUT_FOLDER = "recordings"
MAX_FOLDER_SIZE_BYTES = 48 * 1024 * 1024 * 1024  # 48GB
FILE_DURATION = 10 * 60  # 10 Minutes

# Logging
LOGS_FOLDER = "logs"
if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)
logging.basicConfig(
    filename=os.path.join(LOGS_FOLDER, "error.log"),
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

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
MODEL = "models/12thMar2024/traffic_12thMar2024.tflite"
SCORE_THRESHOLD = 0.3
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


def main(maxFps: str, cameraId, numThreads: int, showPreview: bool):
    try:
        utils.playSound("sounds/startup.mp3", wait=True)

        # Start the server
        apiServer = APIServer()
        apiServer.start()

        # Cleanup old video files
        cleanup = Cleanup(
            folderPath=OUTPUT_FOLDER,
            targetSizeBytes=MAX_FOLDER_SIZE_BYTES,
            apiData=apiServer.data.inferenceData,
        )
        cleanup.removeOldFiles()

        # Start recovery as soon as the program starts
        videoRecovery = VideoRecovery(
            recoveryFolder=RECOVERY_FOLDER,
            outputFolder=OUTPUT_FOLDER,
            apiData=apiServer.data.inferenceData,
            fps=maxFps,
        )
        videoRecovery.recoverVideo()

        # Open input source
        inputSource = InputSource(
            videoSource=cameraId, width=WIDTH, height=HEIGHT, maxFps=maxFps
        )
        inputSource.start()

        # Start up dashcam recording
        dashcam = Dashcam(
            inputSource,
            fileDuration=FILE_DURATION,
            outputFolder=OUTPUT_FOLDER,
            recoveryFolder=None,
            fps=maxFps,
        )
        dashcam.start()

        # Start inference
        inference = Inference(
            inputSource=inputSource,
            indexPriority=[GREEN.index, YELLOW.index, RED.index, OFF.index],
            model=MODEL,
            scoreThreshold=SCORE_THRESHOLD,
            maxResults=MAX_RESULTS,
            numThreads=numThreads,
            actionsDict=ACTIONS_DICT,
            maxFps=maxFps,
            categoriesDeniedList=[OFF.name],
            showPreview=showPreview,
            apiData=apiServer.data.inferenceData,
        )

        # Start light detection
        lightDetection = LightDetection(inputSource=inputSource, apiData=apiServer.data.lightModeData)
        lightDetection.start()

        utils.playSound("sounds/application_start.mp3")

        apiServer.data.inferenceData.status = Status.INFERENCE.value
        while (not inputSource.stopEvent.is_set()) and (not dashcam.stopEvent.is_set()):
            if apiServer.isClientActive() or showPreview:
                inference.infer()
            else:
                time.sleep(1)

            if showPreview and cv2.waitKey(1) == ord("q"):
                break

    except KeyboardInterrupt:
        print("Closing the application...")
    except Exception as e:
        utils.playSound("sounds/error.mp3")
        print(e)
        logging.error(e)
    finally:
        try:
            apiServer.data.inferenceData.status = Status.IDLE.value
            lightDetection.stop()
            inference.destroyWindow()
            inference.stop()
            dashcam.stop()
            inputSource.stop()
        except Exception as e:
            utils.playSound("sounds/error.mp3")
            print(e)
            logging.error(e)

    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--source",
        help="Path to the input video file.",
        required=False,
        default=CAMERA_ID,
    )
    parser.add_argument(
        "--numThreads",
        help="Number of CPU threads to run the model.",
        required=False,
        type=int,
        default=NUM_THREADS,
    )
    parser.add_argument(
        "--maxFps",
        help="Path to the output video file to save the processed frames.",
        required=False,
        type=float,
        default=FPS,
    )
    parser.add_argument(
        "--showPreview",
        help="Show the preview of the video.",
        required=False,
        action="store_true",
    )
    args = parser.parse_args()
    main(
        cameraId=args.source,
        maxFps=args.maxFps,
        numThreads=args.numThreads,
        showPreview=args.showPreview,
    )
    pass
