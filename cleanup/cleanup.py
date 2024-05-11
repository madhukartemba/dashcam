import os
import sys

class Cleanup:
    def __init__(self, folderPath, targetSize):
        self.folderPath = folderPath
        self.targetSize = targetSize

    def getFolderPath(self):
        totalSize = 0
        for dirpath, dirnames, filenames in os.walk(self.folderPath):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                totalSize += os.path.getsize(fp)
        return totalSize

    def removeOldestFiles(self):
        while self.getFolderPath() > self.targetSize:
            files = [(f, os.path.getmtime(os.path.join(self.folderPath, f))) for f in os.listdir(self.folderPath)]
            oldestFile = min(files, key=lambda x: x[1])[0]
            os.remove(os.path.join(self.folderPath, oldestFile))
            print(f"Removed oldest file: {oldestFile}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <folder_path> <target_size_in_bytes>")
        sys.exit(1)

    folderPath = sys.argv[1]
    targetSize = int(sys.argv[2])

    folderManager = Cleanup(folderPath, targetSize)
    folderManager.removeOldestFiles()
