from video_recovery import VideoRecovery
from input_source import InputSource
from dashcam import Dashcam


RECOVERY_FOLDER = 'recovery'
OUTPUT_FOLDER = 'recordings'
FPS = 30.0
CAMERA_ID = 0
WIDTH = 1280
HEIGHT = 720
FILE_DURATION = 600

if __name__ == "__main__":

    # Start recovery as soon as the program starts
    videoRecovery = VideoRecovery(RECOVERY_FOLDER, OUTPUT_FOLDER, FPS)
    videoRecovery.recoverVideo()

    # Open input source
    inputSource = InputSource(CAMERA_ID, WIDTH, HEIGHT)
    inputSource.start()

    # Start up dashcam recording
    dashcam = Dashcam(inputSource, FILE_DURATION, OUTPUT_FOLDER, RECOVERY_FOLDER, FPS)
    dashcam.start()

    
