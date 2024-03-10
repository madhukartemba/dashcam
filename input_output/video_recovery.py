import logging
import cv2
import os
import shutil
import re
from main import APIData, Status
import utils.utils as utils
from input_output.video_maker import VideoMaker


class VideoRecovery:
    def __init__(
        self, recoveryFolder: str, outputFolder: str, apiData: APIData, fps: float = 30.0
    ) -> None:
        self.recoveryFolder = recoveryFolder
        self.outputFolder = outputFolder
        self.fps = fps
        self.apiData = apiData

    def getFrameDimensions(self):
        try:
            image_file = os.path.join(
                self.recoveryFolder, os.listdir(self.recoveryFolder)[0]
            )
            image = cv2.imread(image_file)
            return image.shape[1], image.shape[0]
        except Exception as e:
            print(e)
            logging.error(e)
            return (1280, 720)

    @staticmethod
    def frameNumberSort(fileName):
        match = re.search(r"\d+", fileName)
        if match:
            return int(match.group())
        else:
            return 0

    def recoverVideo(self):

        try:
            if self.apiData:
                self.apiData.status = Status.RECOVERY.value
            if not os.path.exists(self.recoveryFolder):
                print(f"Recovery folder '{self.recoveryFolder}' does not exist.")
                return

            if not os.path.isdir(self.recoveryFolder):
                print(f"Path '{self.recoveryFolder}' is not a directory.")
                return

            if not os.listdir(self.recoveryFolder):
                print(
                    f"Recovery folder '{self.recoveryFolder}' is empty. No images to recover."
                )
                return

            sortedFiles = sorted(
                filter(
                    lambda x: str(x).endswith(".jpg"), os.listdir(self.recoveryFolder)
                ),
                key=VideoRecovery.frameNumberSort,
            )

            width, height = self.getFrameDimensions()
            firstTimestamp = str(
                int(os.path.getmtime(os.path.join(self.recoveryFolder, sortedFiles[0])))
            )

            print("\nStarting recovery...")

            outputFile = os.path.join(self.outputFolder, firstTimestamp)

            videoMaker = VideoMaker(outputFile, width, height, self.fps)

            total_files = len(sortedFiles)

            for i, file in enumerate(sortedFiles, start=1):
                image_path = os.path.join(self.recoveryFolder, file)
                try:
                    image = cv2.imread(image_path)
                    videoMaker.writeFrame(image)
                except Exception as e:
                    print(f"Exception occured while processing image {image_path}")
                    print(e)
                    logging.error(e)

                progress = i / total_files * 100
                if self.apiData:
                    self.apiData.recoveryPercent = progress
                print(f"\rProgress: {progress:.2f}%", end="", flush=True)

            videoMaker.releaseVideo()
            shutil.rmtree(self.recoveryFolder, ignore_errors=True)
            print("\nRecovery completed.\n")
        except Exception as e:
            utils.playSound("sounds/error.mp3")
            print(e)
            logging.error(e)

        pass


if __name__ == "__main__":
    recoveryFolder = "recovery/"
    outputFolder = "outputs/"
    fps = 30.0

    videoRecovery = VideoRecovery(recoveryFolder, outputFolder, None, fps)
    videoRecovery.recoverVideo()
