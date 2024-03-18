import cv2
import os
import shutil
import xml.etree.ElementTree as ET


# Path to the folder containing images
folder_path = 'all'

# Function to adjust contrast
def adjust_contrast(image, alpha):
    # Convert image to YUV color space
    yuv_image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    # Scale the Y (luminance) channel
    yuv_image[:,:,0] = cv2.convertScaleAbs(yuv_image[:,:,0], alpha=alpha)
    # Convert back to BGR color space
    adjusted_image = cv2.cvtColor(yuv_image, cv2.COLOR_YUV2BGR)
    return adjusted_image

# Loop through each file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        # Read the image
        image_path = os.path.join(folder_path, filename)
        image = cv2.imread(image_path)

        # Create slightly higher contrast versions
        high_contrast_image1 = adjust_contrast(image, alpha=1.3)
        high_contrast_image2 = adjust_contrast(image, alpha=1.6)

        # Create slightly lower contrast versions
        low_contrast_image1 = adjust_contrast(image, alpha=0.5)
        low_contrast_image2 = adjust_contrast(image, alpha=0.3)

        # Save the images with new names
        high_contrast_path1 = os.path.join(folder_path, 'high_contrast1_' + filename)
        high_contrast_path2 = os.path.join(folder_path, 'high_contrast2_' + filename)
        low_contrast_path1 = os.path.join(folder_path, 'low_contrast1_' + filename)
        low_contrast_path2 = os.path.join(folder_path, 'low_contrast2_' + filename)

        cv2.imwrite(high_contrast_path1, high_contrast_image1)
        cv2.imwrite(high_contrast_path2, high_contrast_image2)
        cv2.imwrite(low_contrast_path1, low_contrast_image1)
        cv2.imwrite(low_contrast_path2, low_contrast_image2)

        # Copy the associated XML files and update filenames
        xml_path = os.path.join(folder_path, filename.split('.')[0] + '.xml')
        high_contrast_xml_path1 = os.path.join(folder_path, 'high_contrast1_' + filename.split('.')[0] + '.xml')
        high_contrast_xml_path2 = os.path.join(folder_path, 'high_contrast2_' + filename.split('.')[0] + '.xml')
        low_contrast_xml_path1 = os.path.join(folder_path, 'low_contrast1_' + filename.split('.')[0] + '.xml')
        low_contrast_xml_path2 = os.path.join(folder_path, 'low_contrast2_' + filename.split('.')[0] + '.xml')

        shutil.copyfile(xml_path, high_contrast_xml_path1)
        shutil.copyfile(xml_path, high_contrast_xml_path2)
        shutil.copyfile(xml_path, low_contrast_xml_path1)
        shutil.copyfile(xml_path, low_contrast_xml_path2)

        # Update filenames in XML files
        for xml_file in [high_contrast_xml_path1, high_contrast_xml_path2, low_contrast_xml_path1, low_contrast_xml_path2]:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for filename_tag in root.iter('filename'):
                filename_tag.text = os.path.basename(xml_file).replace('.xml', '.jpg')
            tree.write(xml_file)

print("Images and XML files created successfully.")
