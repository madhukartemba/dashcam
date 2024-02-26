from typing import Dict, Tuple, Callable


class Action:
    def __init__(
        self,
        actions: Dict[Tuple[int | None, int | None], Callable[[], None]],
        initialIndex: int | None = None,
    ) -> None:
        self.prevIndex = initialIndex
        self.actions = actions

    def act(self, index):
        if (self.prevIndex, index) in self.actions:
            self.actions[(self.prevIndex, index)]()
        self.prevIndex = index


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
    action_instance = Action(actions_dict)

    # Test the act method
    action_instance.act(1)  # This should do nothing
    action_instance.act(None)  # This will perform action2
    action_instance.act(None)  # This should do nothing
    action_instance.act(0) # This should do nothing
    action_instance.act(1) # This will perform action1
