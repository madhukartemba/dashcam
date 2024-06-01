import logging
from enum import Enum
from datetime import datetime, timedelta
from flask import Flask, jsonify, Response, send_file
import threading
import os
import cv2
from dataclasses import dataclass

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
    def __init__(self, data=data, activeClientThreshold=timedelta(seconds=3)):
        self.data = data
        self.lastCall = datetime.now()
        self.activeClientThreshold = activeClientThreshold
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
                if not os.path.exists("recordings"):
                    return jsonify({"videoNames": []})
                
                videos = os.listdir("recordings")
                return jsonify({"videoNames": videos})
            except Exception as e:
                print(e)
                logging.error(e)
                return str(e), 500

        @self.app.route("/videos/<videoName>/thumbnail", methods=["GET"])
        def getThumbnail(videoName):
            try:
                video_path = os.path.join("recordings", videoName)
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
                video_path = os.path.join("recordings", videoName)
                if not os.path.exists(video_path):
                    return "Video not found", 404
                
                return send_file(video_path, mimetype="video/mkv")
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
