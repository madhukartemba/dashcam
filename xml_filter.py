import os
import xml.etree.ElementTree as ET

# Path to the directory containing XML files
directory_path = 'totalLabelledFrames'

# List all XML files in the directory
xml_files = [file for file in os.listdir(directory_path) if file.endswith('.xml')]

# Modify each XML file
for file_name in xml_files:
    file_path = os.path.join(directory_path, file_name)
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Find and remove <object> elements with name 'off'
    for obj in root.findall('object'):
        if obj.find('name').text == 'off':
            root.remove(obj)
    
    # Delete the file if no objects are left
    if len(root.findall('object')) == 0:
        print(file_path)
        os.remove(file_path)
    else:
        # Save the modified XML file
        tree.write(file_path)
