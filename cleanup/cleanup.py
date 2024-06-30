import logging
import os
import sys

from api_server import InferenceData, Status
from constants import CACHE_FOLDER, OUTPUT_FOLDER
from storage.storage import Storage


class Cleanup:
    def __init__(self, folderPath, cachePath, targetSizeBytes, apiData: InferenceData):
        self.folderPath = folderPath
        self.cachePath = cachePath
        self.targetSizeBytes = targetSizeBytes
        self.apiData = apiData
        self.storage = Storage(folderPath, cachePath)

    def getTotalSize(self):
        totalSize = 0
        for dirpath, dirnames, filenames in os.walk(self.folderPath):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                totalSize += os.path.getsize(fp)

        for dirpath, dirnames, filenames in os.walk(self.cachePath):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                totalSize += os.path.getsize(fp)

        return totalSize

    def removeOldFiles(self):
        try:
            totalSize = self.getTotalSize()

            overflowSize = totalSize - self.targetSizeBytes

            while totalSize > self.targetSizeBytes:
                if self.apiData:
                    newOverflowSize = totalSize - self.targetSizeBytes
                    self.apiData.cleanupPercent = (
                        1 - newOverflowSize / overflowSize
                    ) * 100

                files = [
                    (f, os.path.getmtime(os.path.join(self.folderPath, f)))
                    for f in os.listdir(self.folderPath)
                ]
                oldestFile = min(files, key=lambda x: x[1])[0]
                os.remove(os.path.join(self.folderPath, oldestFile))
                self.storage.deleteVideoThumbnail(oldestFile)
                print(f"Removed oldest file: {oldestFile}")
                totalSize = self.getTotalSize()
        except Exception as e:
            print(e)
            logging.error(e)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <folder_path> <target_size_in_bytes>")
        sys.exit(1)

    folderPath = sys.argv[1]
    targetSize = int(sys.argv[2])

    folderManager = Cleanup(folderPath, targetSize)
    folderManager.removeOldFiles()
