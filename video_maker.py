import cv2


class VideoMaker:
    def __init__(self, output_file: str, width: int, height: int) -> None:
        fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
        if not output_file.endswith(".mp4"):
            output_file = output_file + ".mp4"
        self.output_file = output_file
        self.width = width
        self.height = height
        self.out = cv2.VideoWriter(
            self.output_file, fourcc, 30.0, (width, height), isColor=True
        )

    def writeFrame(self, image):
        self.out.write(cv2.resize(image, (self.width, self.height)))

    def releaseVideo(self):
        self.out.release()
