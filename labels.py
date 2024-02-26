class Label:
    def __init__(self, index, name) -> None:
        self.index = index
        self.name = name
        pass


class Labels:
    def __init__(self) -> None:
        self.indexToLabel = {}
        self.nameToLabel = {}
        pass

    def addLabels(self, *labels: Label):
        for label in labels:
            self.indexToLabel[label.index] = label
            self.nameToLabel[label.name] = label
        pass

    def getLabelFromIndex(self, index):
        return self.indexToLabel[index]

    def getLabelFromName(self, name):
        return self.nameToLabel[name]


def main():
    label1 = Label(1, "Label1")
    label2 = Label(2, "Label2")
    label3 = Label(3, "Label3")

    labels = Labels()
    labels.addLabels(label1, label2, label3)

    # Test getLabelFromIndex
    index = 2
    label = labels.getLabelFromIndex(index)
    print(f"Label with index {index}: {label.name}")

    # Test getLabelFromName
    name = "Label3"
    label = labels.getLabelFromName(name)
    print(f"Label with name {name}: {label.index}")

    # Test getLabelFromIndex which does not exist
    index = 4
    try:
        label = labels.getLabelFromIndex(index)
        print(f"Label with index {index}: {label.name}")
    except:
        print(f"Label index {index} does not exist")

    # Test getLabelFromIndex which does not exist
    name = 'Label4'
    try:
        label = labels.getLabelFromName(name)
        print(f"Label with name {name}: {label.name}")
    except:
        print(f"Label name {name} does not exist")


if __name__ == "__main__":
    main()
