import cv2


class VideoMaker:
    def __init__(self, outputFile: str, width: int, height: int, fps: float = 30.0) -> None:
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        if not outputFile.endswith(".mkv"):
            outputFile = outputFile + ".mkv"
        self.outputFile = outputFile
        self.width = width
        self.height = height
        self.out = cv2.VideoWriter(
            self.outputFile, fourcc, fps, (width, height), isColor=True
        )

    def writeFrame(self, image):
        self.out.write(cv2.resize(image, (self.width, self.height)))

    def releaseVideo(self):
        self.out.release()
