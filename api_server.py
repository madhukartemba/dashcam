from enum import Enum
import time
from flask import Flask, jsonify
import threading
from dataclasses import dataclass


class APIServer:
    def __init__(self, data):
        self.data = data
        self.app = Flask(__name__)
        self.thread = None

        @self.app.route("/", methods=["GET"])
        def getData():
            return jsonify(self.data)

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
