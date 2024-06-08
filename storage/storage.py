import logging
import os
import cv2
import shutil


class Storage:
    def __init__(self, output_folder, cache_folder):
        self.output_folder = output_folder
        self.cache_folder = cache_folder

        # Ensure the cache folder exists
        if not os.path.exists(self.cache_folder):
            os.makedirs(self.cache_folder)

    def getVideoThumbnail(self, video_name: str):
        video_path = os.path.join(self.output_folder, video_name)
        image_name, _ = os.path.splitext(video_name)
        thumbnail_path = os.path.join(self.cache_folder, f"{image_name}.jpg")

        # Check if the thumbnail is already cached
        if os.path.exists(thumbnail_path):
            with open(thumbnail_path, "rb") as f:
                return f.read()

        if not os.path.exists(video_path):
            return None

        # Generate the thumbnail if not cached
        try:
            cap = cv2.VideoCapture(video_path)
            success, frame = cap.read()
            cap.release()

            if not success:
                return None

            # Resize the frame to 480 x 270
            resized_frame = cv2.resize(frame, (480, 270))

            # Encode the resized frame as a JPEG image
            _, buffer = cv2.imencode(".jpg", resized_frame)
            thumbnail_bytes = buffer.tobytes()

            # Save the thumbnail to the cache folder
            with open(thumbnail_path, "wb") as f:
                f.write(thumbnail_bytes)

            return thumbnail_bytes

        except Exception as e:
            print(e)
            # Don't log this exception
            return None

    def deleteVideoThumbnail(self, video_name: str):
        image_name, _ = os.path.splitext(video_name)
        thumbnail_path = os.path.join(self.cache_folder, f"{image_name}.jpg")

        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
            return True
        return False

    def deleteCache(self):
        if os.path.exists(self.cache_folder):
            shutil.rmtree(self.cache_folder)
            print(f"Cache folder '{self.cache_folder}' deleted successfully.")
            os.makedirs(self.cache_folder)
            print(f"Cache folder '{self.cache_folder}' recreated successfully.")
        else:
            print(f"Cache folder '{self.cache_folder}' does not exist.")
