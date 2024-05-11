import os
import sys

from api_server import APIData, Status


class Cleanup:
    def __init__(self, folderPath, targetSizeBytes, apiData: APIData):
        self.folderPath = folderPath
        self.targetSizeBytes = targetSizeBytes
        self.apiData = apiData

    def getFolderSize(self):
        totalSize = 0
        for dirpath, dirnames, filenames in os.walk(self.folderPath):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                totalSize += os.path.getsize(fp)
        return totalSize

    def removeOldFiles(self):
        if self.apiData:
            self.apiData.status = Status.CLEANUP.value
            self.apiData.cleanupPercent = 0

        folderSize = self.getFolderSize()

        overflowSize = folderSize - self.targetSizeBytes

        while folderSize > self.targetSizeBytes:
            if self.apiData:
                newOverflowSize = folderSize - self.targetSizeBytes
                self.apiData.cleanupPercent = (1 - newOverflowSize / overflowSize) * 100

            files = [
                (f, os.path.getmtime(os.path.join(self.folderPath, f)))
                for f in os.listdir(self.folderPath)
            ]
            oldestFile = min(files, key=lambda x: x[1])[0]
            os.remove(os.path.join(self.folderPath, oldestFile))
            print(f"Removed oldest file: {oldestFile}")
            folderSize = self.getFolderSize()

        if self.apiData:
            self.apiData.status = Status.IDLE.value
            self.apiData.cleanupPercent = 100


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <folder_path> <target_size_in_bytes>")
        sys.exit(1)

    folderPath = sys.argv[1]
    targetSize = int(sys.argv[2])

    folderManager = Cleanup(folderPath, targetSize)
    folderManager.removeOldFiles()
