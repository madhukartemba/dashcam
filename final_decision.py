from tflite_support.task import processor
import utils


class FinalDecision:
    def __init__(self, indexPriority: list[int], minCount=2) -> None:
        self.minCount: int = minCount
        self.count: int = 0
        self.prevIndex: int = -1
        self.indexPriority = indexPriority
        pass

    def prioritySort(self, detections: list[processor.Detection]):
        return sorted(
            detections,
            key=lambda x: self.indexPriority.index(utils.getCategory(x).index),
        )
    
    def updateMinCount(self, minCount):
        self.minCount = minCount

    def getDecision(self, detections: list[processor.Detection]):

        if len(detections) == 0:
            return None

        detection = self.prioritySort(detections)[0]

        if detection == None:
            self.count = 0
            self.prevIndex = -1
            return None

        index = utils.getCategory(detection).index

        if self.prevIndex == -1 or self.prevIndex != index:
            self.count = 1
        else:
            self.count += 1

        self.prevIndex = index

        if self.count >= self.minCount:
            return detection
        else:
            return None


def main():
    # Example detection indices and categories
    indices = [1, 2, 3, 3, 2, 3, 2, 2, 2]
    categories = [
        "Cat1",
        "Cat2",
        "Cat3",
        "Cat3",
        "Cat2",
        "Cat3",
        "Cat2",
        "Cat2",
        "Cat2",
    ]

    # Create example detections
    detections = [
        processor.Detection(
            bounding_box=processor.BoundingBox(0, 0, 800, 600),
            categories=[processor.Category(i, 0.5, cat, cat)],
        )
        for i, cat in zip(indices, categories)
    ]

    # Create an instance of FinalDecision
    index_priority = [3, 2, 1]
    final_decision = FinalDecision(index_priority, minCount=2)

    # Get the decision based on detections
    for index, detection in enumerate(detections):
        decision = final_decision.getDecision([detection])
        if decision:
            print(f"Decision: {utils.getCategory(decision).index} for index {index}")
        else:
            print(f"No decision made for index {index}")

    # Priority sort test
    priority_decisions = final_decision.prioritySort(detections)
    sorted_indices = [
        utils.getCategory(decision).index for decision in priority_decisions
    ]
    print(sorted_indices)


if __name__ == "__main__":
    main()
