# Copyright 2021 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Main script to run the object detection routine."""
import argparse

import cv2
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision
import utils.utils as utils
import input_output.input_source as input_source


def run(
    model: str,
    video_file: str,
    width: int,
    height: int,
    num_threads: int,
    enable_edgetpu: bool,
    output_file: str,
) -> None:
    """Run object detection on each frame of a video and save the processed frames in a new video file.

    Args:
        model: Name of the TFLite object detection model.
        video_file: Path to the input video file.
        width: The width of the frame captured from the video.
        height: The height of the frame captured from the video.
        num_threads: The number of CPU threads to run the model.
        enable_edgetpu: True/False whether the model is an EdgeTPU model.
        output_file: Path to the output video file to save the processed frames.
    """

    # Initialize video capture from the input video file
    frame_count = 0
    current_frame = 0
    if video_file == None:
        inputSource = input_source.InputSource(0, width, height)
    else:
        inputSource = input_source.InputSource(video_file)
        frame_count = inputSource.frameCount
        width, height = inputSource.getDimensions()

    # Initialize video writer for the output video file

    fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
    out = cv2.VideoWriter(output_file, fourcc, 30.0, (width, height), isColor=True)

    # Initialize the object detection model
    base_options = core.BaseOptions(
        file_name=model, use_coral=enable_edgetpu, num_threads=num_threads
    )
    detection_options = processor.DetectionOptions(max_results=3, score_threshold=0.3)
    options = vision.ObjectDetectorOptions(
        base_options=base_options, detection_options=detection_options
    )
    detector = vision.ObjectDetector.create_from_options(options)

    # Continuously capture frames from the video and run inference
    while inputSource.isCaptureOpen():

        image = inputSource.refreshFrame()

        # Convert the image from BGR to RGB as required by the TFLite model.
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Create a TensorImage object from the RGB image.
        input_tensor = vision.TensorImage.create_from_array(rgb_image)

        # Run object detection estimation using the model.
        detection_result = detector.detect(input_tensor)

        # Draw keypoints and edges on input image
        image = utils.visualize(image, detection_result)

        # Write the processed frame to the output video file
        out.write(cv2.resize(image, (width, height)))

        # Print completion progress
        if frame_count > 0:
            current_frame += 1
            progress = (current_frame / frame_count) * 100
            print(
                f"\rProcessing frame {current_frame}/{frame_count} ({progress:.2f}%)",
                end="",
                flush=True,
            )

        # Show the processed frame (optional)
        cv2.imshow("object_detector", image)

        # Stop the program if the ESC key is pressed.
        if cv2.waitKey(1) == 27:
            break

    inputSource.releaseCapture()
    out.release()
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--model",
        help="Path of the object detection model.",
        required=False,
        default="detect.tflite",
    )
    parser.add_argument(
        "--inputFile",
        help="Path to the input video file.",
        required=False,
        type=str,
        default=None,
    )
    parser.add_argument(
        "--frameWidth",
        help="Width of frame to capture from video.",
        required=False,
        type=int,
        default=1280,
    )
    parser.add_argument(
        "--frameHeight",
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
        default=4,
    )
    parser.add_argument(
        "--enableEdgeTPU",
        help="Whether to run the model on EdgeTPU.",
        action="store_true",
        required=False,
        default=False,
    )
    parser.add_argument(
        "--outputFile",
        help="Path to the output video file to save the processed frames.",
        required=True,
    )
    args = parser.parse_args()

    run(
        args.model,
        args.inputFile,
        args.frameWidth,
        args.frameHeight,
        args.numThreads,
        args.enableEdgeTPU,
        args.outputFile,
    )


if __name__ == "__main__":
    main()
