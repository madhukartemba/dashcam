from typing import Dict, Tuple, Callable


class Actions:
    def __init__(
        self,
        actions: Dict[Tuple[int | None, int | None], Callable[[], None]],
        bufferSize: int = 8,
        initialIndex: int | None = None,
    ) -> None:
        self.prevIndex = initialIndex
        self.actions = actions
        self.noneCount = 0
        self.bufferSize = bufferSize

    def updateBufferSize(self, bufferSize):

        if self.noneCount > bufferSize:
            self.noneCount = self.bufferSize
            self.prevIndex = None

        self.bufferSize = bufferSize

    def act(self, index: int | None):

        if (self.prevIndex, index) in self.actions:
            self.actions[(self.prevIndex, index)]()

        if index == None:
            self.noneCount += 1
            if self.noneCount > self.bufferSize:
                self.noneCount = self.bufferSize
                self.prevIndex = None
        else:
            self.prevIndex = index
            self.noneCount = 0


if __name__ == "__main__":

    def action1():
        print("Performing action 1...")

    def action2():
        print("Performing action 2...")

    # Define a dictionary of actions
    actions_dict: Dict[Tuple[int | None, int | None], (Callable[[], None])] = {
        (0, 1): action1,
        (1, None): action2,
    }

    # Create an instance of the Action class
    action_instance = Actions(actions_dict)

    # Test the act method
    action_instance.act(1)  # This should do nothing
    action_instance.act(None)  # This will perform action2
    action_instance.act(None)  # This should do nothing
    action_instance.act(0)  # This should do nothing
    action_instance.act(1)  # This will perform action1
