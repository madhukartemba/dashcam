import cv2
import os
import time
import re
from video_maker import VideoMaker


class VideoRecovery:
    def __init__(
        self, recoveryFolder: str, outputFolder: str, fps: float = 30.0
    ) -> None:
        self.recoveryFolder = recoveryFolder
        self.outputFolder = outputFolder
        self.fps = fps

    def getFrameDimensions(self):
        image_file = os.path.join(
            self.recoveryFolder, os.listdir(self.recoveryFolder)[0]
        )
        image = cv2.imread(image_file)
        return image.shape[1], image.shape[0]

    @staticmethod
    def frameNumberSort(fileName):
        match = re.search(r"\d+", fileName)
        if match:
            return int(match.group())
        else:
            return 0

    def recoverVideo(self):

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

        sorted_files = list(
            filter(
                lambda x: str(x).endswith(".jpg"),
                sorted(
                    os.listdir(self.recoveryFolder), key=VideoRecovery.frameNumberSort
                ),
            )
        )

        width, height = self.getFrameDimensions()
        firstTimestamp = str(
            int(os.path.getmtime(os.path.join(self.recoveryFolder, sorted_files[0])))
        )
        outputFile = os.path.join(self.outputFolder, firstTimestamp)

        videoMaker = VideoMaker(outputFile, width, height, self.fps)

        for file in sorted_files:
            print(file)
            image_path = os.path.join(self.recoveryFolder, file)
            image = cv2.imread(image_path)
            videoMaker.writeFrame(image)

        videoMaker.releaseVideo()


if __name__ == "__main__":
    recoveryFolder = "recovery/"
    outputFolder = "outputs/"
    fps = 30.0

    videoRecovery = VideoRecovery(recoveryFolder, outputFolder, fps)
    videoRecovery.recoverVideo()
