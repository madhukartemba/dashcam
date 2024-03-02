import cv2
import os


def save_frames(video_path, output_folder):
    print('running')
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_div = 10
    current_frame = 0
    frame_number = 0

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    while cap.isOpened():
        # Read a frame from the video
        ret, frame = cap.read()

        if not ret:
            break

        # Save the frame to the output folder
        if current_frame % frame_div == 0:
            frame_path = os.path.join(output_folder, f"frame_{frame_number}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_number += 1

        # Print progress percentage
        progress = (current_frame + 1) * 100 / total_frames
        print(f"Progress: {progress:0.3f}%", end="\r")

        current_frame += 1

    print('finish')

    # Release the video capture object
    cap.release()


if __name__ == "__main__":
    video_path = "videos/combinedOutput1.mp4"
    output_folder = "frames/"
    save_frames(video_path, output_folder)
