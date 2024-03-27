import logging
from enum import Enum
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


# API Data
@dataclass
class APIData:
    status: str
    trafficLightColor: str
    recoveryPercent: int
    fps: int


apiData = APIData(
    status=Status.IDLE.value, trafficLightColor=None, recoveryPercent=0, fps=0
)


class APIServer:
    def __init__(self, data=apiData):
        self.data = data
        self.app = Flask(__name__)
        self.thread = None

        @self.app.route("/", methods=["GET"])
        def getData():
            try:
                return jsonify(self.data)
            except Exception as e:
                print(e)
                logging.error(e)
                return str(e), 500

        @self.app.route("/videos", methods=["GET"])
        def getVideos():
            try:
                videos = os.listdir("recordings")
                return jsonify(videos)
            except Exception as e:
                print(e)
                logging.error(e)
                return str(e), 500

        @self.app.route("/videos/<videoName>", methods=["GET"])
        def getThumbnail(videoName):
            try:
                video_path = os.path.join("recordings", videoName)
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

        @self.app.route("/videos/<videoName>/source", methods=["GET"])
        def getVideoSource(videoName):
            try:
                video_path = os.path.join("recordings", videoName)
                return send_file(video_path, mimetype="video/mkv")
            except Exception as e:
                print(e)
                logging.error(e)
                return str(e), 500

    def start(self):
        def run_flask():
            self.app.run(host="0.0.0.0", threaded=True)

        self.thread = threading.Thread(target=run_flask)
        self.thread.start()


if __name__ == "__main__":

    @dataclass
    class APIDataExample:
        status: str
        trafficLightColor: str
        recoveryPercent: int
        fps: int

    data = APIDataExample(
        status="idle", trafficLightColor=None, recoveryPercent=0, fps=0
    )
    api = APIServer(data)
    api.start()
