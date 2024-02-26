from tflite_support.task import processor


class DetectionFilter:
    def __init__(self, width: int, height: int, maxAreaDivisor: int = 8) -> None:
        self.width = width
        self.height = height
        self.maxAreaDivisor = maxAreaDivisor
        self.maxArea = (width * height) / maxAreaDivisor

    def filterFunction(self, detection: processor.Detection):
        area = detection.bounding_box.width * detection.bounding_box.height
        return area <= self.maxArea

    def filter(self, detectionResult: processor.DetectionResult):
        return list(filter(self.filterFunction, detectionResult.detections))


if __name__ == "__main__":
    f = DetectionFilter(1280, 720)
    print(f.maxArea)

    # Create some example detections
    d1 = processor.Detection(
        bounding_box=processor.BoundingBox(0, 0, 200, 100),
        categories=[processor.Category(0, 0.5, "testCat1", "Cat1")],
    )
    d2 = processor.Detection(
        bounding_box=processor.BoundingBox(0, 0, 50, 50),
        categories=[processor.Category(0, 0.5, "testCat2", "Cat2")],
    )
    d3 = processor.Detection(
        bounding_box=processor.BoundingBox(0, 0, 800, 600),
        categories=[processor.Category(0, 0.5, "testCat3", "Cat3")],
    )

    # Create a DetectionResult with the example detections
    detectionResult = processor.DetectionResult(detections=[d1, d2, d3])

    # Filter the detections
    filtered_detections = f.filter(detectionResult)

    # Print the filtered detections
    print("Filtered Detections:")
    for detection in filtered_detections:
        print(f"Area: {detection.bounding_box.width * detection.bounding_box.height}")
