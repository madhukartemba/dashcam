import argparse
import cv2
import utils.utils as utils
from input_output.input_source import InputSource
from input_output.video_maker import VideoMaker
from inference.inference_engine import InferenceEngine
from inference.detection_filter import DetectionFilter
from inference.final_decision import FinalDecision
from inference.actions import Actions
from inference.labels import Labels, Label

# Define the expected FPS
FPS = 53

# Define all the labels here
red = Label(0, "red")
green = Label(1, "green")
yellow = Label(2, "yellow")
off = Label(3, "off")

# Add all the labels here
labels = Labels()
labels.addLabels(red, yellow, green, off)

# Define state change actions
actionsDict = {
    (red.index, green.index): lambda: utils.playSound("sounds/key24.mp3"),
    (yellow.index, green.index): lambda: utils.playSound("sounds/key24.mp3"),
    (green.index, yellow.index): lambda: utils.playSound("sounds/key21.mp3"),
    (None, yellow.index): lambda: utils.playSound("sounds/key21.mp3"),
    (green.index, red.index): lambda: utils.playSound("sounds/key18.mp3"),
    (yellow.index, red.index): lambda: utils.playSound("sounds/key18.mp3"),
    (None, red.index): lambda: utils.playSound("sounds/key18.mp3"),
}

# actionsDict = {
#     (red.index, green.index): lambda: print("green light! (from red)"),
#     (yellow.index, green.index): lambda: print("green light! (from yellow)"),
#     (green.index, yellow.index): lambda: print("yellow light! (from green)"),
#     (None, yellow.index): lambda: print("yellow light! (from none)"),
#     (green.index, red.index): lambda: print("red light! (from green)"),
#     (yellow.index, red.index): lambda: print("red light! (from yellow)"),
#     (None, red.index): lambda: print("red light! (from none)"),
# }


def run(
    model: str,
    source: str,
    width: int,
    height: int,
    numThreads: int,
    outputFile: str | None,
    labels: Labels,
    actionsDict,
):
    if source == None:
        inputSource = InputSource(0, width, height)
    else:
        inputSource = InputSource(source)

    if outputFile != None:
        videoMaker = VideoMaker(outputFile, inputSource.width, inputSource.height)
    else:
        videoMaker = None

    inferenceEngine = InferenceEngine(model, [off.name], numThreads, scoreThreshold=0.3)

    detectionFilter = DetectionFilter(inputSource.width, inputSource.height)

    finalDecision = FinalDecision(
        [green.index, yellow.index, red.index, off.index], minCount=max(1, FPS * 2 / 3)
    )

    actions = Actions(actionsDict, bufferSize=10 * FPS)

    while inputSource.isCaptureOpen():
        image = inputSource.refreshFrame()
        fps = inputSource.getFps()

        detectionResult = inferenceEngine.getDetections(image)

        detections = detectionFilter.filter(detectionResult)

        detection = finalDecision.getDecision(detections)

        actions.act(
            index=utils.getCategory(detection).index if detection is not None else None
        )

        # Show FPS text
        fps_text = "FPS = {:.1f}".format(fps)
        utils.putText(image, fps_text, (24, 20))

        if detection != None:
            image = utils.visualize(image, [detection])

        if videoMaker:
            videoMaker.writeFrame(image)

        cv2.imshow("object_detector", image)

        if cv2.waitKey(1) == 27:
            break

    if videoMaker:
        videoMaker.releaseVideo()
    cv2.destroyAllWindows()

    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--model",
        help="Path of the object detection model.",
        required=False,
        default="models/3rdMar2024/traffic_3rdMar2024.tflite",
    )
    parser.add_argument(
        "--source",
        help="Path to the input video file.",
        required=False,
        type=str,
        default=None,
    )
    parser.add_argument(
        "--width",
        help="Width of frame to capture from video.",
        required=False,
        type=int,
        default=1280,
    )
    parser.add_argument(
        "--height",
        help="Height of frame to capture from video.",
        required=False,
        type=int,
        default=720,
    )
    parser.add_argument(
        "--numThreads",
        help="Number of CPU threads to run the model.",
        required=False,
        type=int,
        default=2,
    )
    parser.add_argument(
        "--output",
        help="Path to the output video file to save the processed frames.",
        required=False,
        type=str,
        default=None,
    )
    args = parser.parse_args()

    run(
        args.model,
        args.source,
        args.width,
        args.height,
        args.numThreads,
        args.output,
        labels,
        actionsDict,
    )
    pass
