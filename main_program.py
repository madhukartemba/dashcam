import argparse
import cv2
import utils
from input_source import InputSource
from video_maker import VideoMaker
from inference_engine import InferenceEngine
from detection_filter import DetectionFilter
from final_decision import FinalDecision


def run(
    model: str,
    source: str,
    width: int,
    height: int,
    numThreads: int,
    outputFile: str | None,
):
    if source == None:
        inputSource = InputSource(0, width, height)
    else:
        inputSource = InputSource(source)

    if outputFile != None:
        videoMaker = VideoMaker(outputFile, inputSource.width, inputSource.height)
    else:
        videoMaker = None

    inferenceEngine = InferenceEngine(model, numThreads, score_threshold=0.1)

    detectionFilter = DetectionFilter(inputSource.width, inputSource.height)

    while inputSource.isCaptureOpen():
        image = inputSource.getImage()

        detectionResult = inferenceEngine.getDetections(image)

        image = utils.visualize(image, detectionResult)

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
        default="traffic_light.tflite",
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
    )
    pass
