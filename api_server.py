import logging
from enum import Enum
from datetime import datetime, timedelta
from flask import Flask, jsonify, Response, send_file
import threading
import os
import cv2
from dataclasses import dataclass
from constants import (
    LOG_FILENAME,
    LOGS_FOLDER,
    MAX_FOLDER_SIZE_BYTES,
    OUTPUT_FOLDER,
    VERSION,
)
from input_output.input_source import InputSource


log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


class Status(Enum):
    IDLE = "idle"
    RECOVERY = "recovery"
    INFERENCE = "inference"
    CLEANUP = "cleanup"


class LightMode(Enum):
    BRIGHT = "bright"
    DARK = "dark"


@dataclass
class InferenceData:
    status: str
    trafficLightColor: str
    recoveryPercent: int
    cleanupPercent: int
    fps: int


@dataclass
class LightModeData:
    lightMode: str


@dataclass
class Data:
    inferenceData: InferenceData
    lightModeData: LightModeData


# Initialize the combined data object
data = Data(
    inferenceData=InferenceData(
        status=Status.IDLE.value,
        trafficLightColor=None,
        recoveryPercent=0,
        fps=0,
        cleanupPercent=0,
    ),
    lightModeData=LightModeData(
        lightMode=LightMode.DARK.value,
    ),
)


class APIServer:
    def __init__(self, inputSource:InputSource, data=data, activeClientThreshold=timedelta(seconds=3)):
        self.data = data
        self.lastCall = datetime.now()
        self.activeClientThreshold = activeClientThreshold
        self.inputSource = inputSource
        self.app = Flask(__name__)
        self.thread = None

        @self.app.route("/", methods=["GET"])
        def getInferenceData():
            try:
                self.lastCall = datetime.now()
                return jsonify(self.data.inferenceData)
            except Exception as e:
                print(e)
                logging.error(e)
                return str(e), 500

        @self.app.route("/lightMode", methods=["GET"])
        def getLightModeData():
            try:
                return jsonify(self.data.lightModeData)
            except Exception as e:
                print(e)
                logging.error(e)
                return str(e), 500

        @self.app.route("/videos", methods=["GET"])
        def getVideos():
            try:
                if not os.path.exists(OUTPUT_FOLDER):
                    return jsonify({"videoNames": []})

                videos = os.listdir(OUTPUT_FOLDER)
                return jsonify({"videoNames": videos})
            except Exception as e:
                print(e)
                logging.error(e)
                return str(e), 500

        @self.app.route("/videos/<videoName>/thumbnail", methods=["GET"])
        def getThumbnail(videoName):
            try:
                video_path = os.path.join(OUTPUT_FOLDER, videoName)
                if not os.path.exists(video_path):
                    return "Video not found", 404

                cap = cv2.VideoCapture(video_path)
                success, frame = cap.read()
                cap.release()

                if success:
                    _, buffer = cv2.imencode(".jpg", frame)
                    return Response(buffer.tobytes(), mimetype="image/jpeg")
                else:
                    return "Failed to generate thumbnail", 500
            except Exception as e:
                print(e)
                logging.error(e)
                return str(e), 500

        @self.app.route("/videos/<videoName>", methods=["GET"])
        def getVideoSource(videoName):
            try:
                video_path = os.path.join(OUTPUT_FOLDER, videoName)
                if not os.path.exists(video_path):
                    return "Video not found", 404

                return send_file(video_path, mimetype="video/mkv")
            except Exception as e:
                print(e)
                logging.error(e)
                return str(e), 500

        @self.app.route("/info", methods=["GET"])
        def getInfo():
            try:
                currentSize = 0
                if os.path.exists(OUTPUT_FOLDER):
                    for dirpath, dirnames, filenames in os.walk(OUTPUT_FOLDER):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            currentSize += os.path.getsize(fp)

                info = {
                    "version": VERSION,
                    "currentRecordingsSize": currentSize,
                    "maxRecordingsSize": MAX_FOLDER_SIZE_BYTES,
                }
                return jsonify(info)
            except Exception as e:
                print(e)
                logging.error(e)
                return str(e), 500

        @self.app.route("/logs", methods=["GET"])
        def getLogs():
            try:
                log_file_path = os.path.join(LOGS_FOLDER, LOG_FILENAME)
                if not os.path.exists(log_file_path):
                    return "Log file not found", 404

                with open(log_file_path, "r") as log_file:
                    log_contents = log_file.read()

                return Response(log_contents, mimetype="text/plain")
            except Exception as e:
                print(e)
                logging.error(e)
                return str(e), 500
        @self.app.route('/currentImage', ['GET'])
        def getCurrentImage():
            try:
                image = self.inputSource.getImage()
                _, buffer = cv2.imencode(".jpg", image)
                return Response(buffer.tobytes(), mimetype="image/jpeg")
            except Exception as e:
                print(e)
                logging.error(e)
                return str(e), 500

    def isClientActive(self):
        delta = datetime.now() - self.lastCall
        return delta < self.activeClientThreshold

    def start(self):
        def run_flask():
            self.app.run(host="0.0.0.0", threaded=True)

        self.thread = threading.Thread(target=run_flask)
        self.thread.start()


if __name__ == "__main__":

    api = APIServer(activeClientThreshold=timedelta(seconds=10))
    api.start()
