import os
import xml.etree.ElementTree as ET

labels = ['off', 'green', 'red', 'yellow']

def contains_invalid_objects(xml_file_path, labels):
    """
    Check if an XML file contains objects not in the specified list of labels.

    Args:
    - xml_file_path (str): Path to the XML file.
    - labels (list): List of valid labels.

    Returns:
    - bool: True if the XML file contains invalid objects, False otherwise.
    """
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    
    for obj in root.findall('object'):
        name = obj.find('name').text
        if name not in labels:
            return True  # Invalid object found
    return False  # All objects are valid

# Path to the directory containing XML files
directory_path = 'totalLabelledFrames'

# List all XML files in the directory
xml_files = [file for file in os.listdir(directory_path) if file.endswith('.xml')]

# Verify each XML file
for file_name in xml_files:
    file_path = os.path.join(directory_path, file_name)
    if contains_invalid_objects(file_path, labels):
        print(f"File '{file_name}' contains invalid objects.")
