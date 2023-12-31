import cv2
import datetime
from datetime import datetime


tc_bounding_boxes = {
    "tc": [[[45, 135], [201, 135], [201, 171], [45, 171]], int],
    "surname": [[[215, 205], [295, 205], [295, 241], [215, 241]], str],
    "name": [[[216, 260], [338, 260], [338, 290], [216, 290]], str],
    "dob": [[[214, 312], [322, 312], [322, 342], [214, 342]], datetime],
    "serie_no": [[[212, 364], [324, 364], [324, 394], [212, 394]], str]
}

id_back_boxes = {
    "mother_name": [[[162, 120], [238, 120], [238, 150], [162, 150]] ,str],
    "father_name": [[[164, 176], [272, 176], [272, 206], [164, 206]], str]
}

# Function to calculate the size of a bounding box
def box_size(box):
    return (box[1][0] - box[0][0]) * (box[2][1] - box[1][1])


def filter_boxes(easyocr_result, min_bounding_box_size=100, min_text_confidence=0.60):
    # Define thresholds for bounding box size and text confidence
    min_bounding_box_size = 100  # Adjust as needed
    min_text_confidence = 0.60  # Adjust as needed

    # Filter the results based on size and confidence
    filtered_results = [
        (box, text, confidence) for (box, text, confidence) in easyocr_result
        if box_size(box) >= min_bounding_box_size and confidence >= min_text_confidence
    ]
    return filtered_results


def resize_image(image_path):
    # Read the image
    original_image = cv2.imread(image_path)

    # Convert the image to grayscale
    # gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    # Resize the image to 640x480
    resized_image = cv2.resize(original_image, (640, 480))

    return resized_image


# Function to calculate the Euclidean distance between the centers of two bounding boxes
def calculate_distance(bbox1, bbox2):
    """
    Calculate the Euclidean distance between the centers of two bounding boxes.
    """
    x1_center = (bbox1[0][0] + bbox1[1][0]) / 2
    y1_center = (bbox1[0][1] + bbox1[2][1]) / 2
    x2_center = (bbox2[0][0] + bbox2[1][0]) / 2
    y2_center = (bbox2[0][1] + bbox2[2][1]) / 2

    distance = ((x1_center - x2_center) ** 2 + (y1_center - y2_center) ** 2) ** 0.5
    return distance


# Function to check if two bounding boxes are in the same zone
def is_same_zone(bbox1, bbox2, coord_threshold=35):
    cord1 = [bbox1[0], bbox1[3]]
    cord2 = [bbox2[0], bbox2[3]]
    for coordinate1, coordinate2 in zip(cord1, cord2):
        for x1, x2 in zip(coordinate1, coordinate2):
            if abs(x1 - x2) > coord_threshold:
                return False
    return True


# Function to find matching text between EasyOCR results and reference bounding boxes
def find_matching_text(easyocr_results, bounding_boxes):
    matches = []

    for key, reference_bbox in bounding_boxes.items():
        for result in easyocr_results:
            if is_same_zone(result[0], reference_bbox[0], coord_threshold=35):
                matches.append([key, result[1], result[0], result[2], reference_bbox[1]])
    return matches


# Function to convert string to int, date or string
def convert_to_type(value):
    if value.isdigit():
        return int(value)
    elif value.replace('.', '', 1).isdigit():  # Check for float with one decimal point
        return float(value)
    else:
        try:
            date_obj = datetime.strptime(value, "%d.%m.%Y")
            return date_obj
        except ValueError:
            return value


list_check = ['Adi', 'surname', 'soyadi', "adı", "dogum", "date", "date of birth", "given", "given name", "seri no", "son",]  # Assuming 'Adi' should be a string in the list


def remove_unwanted_entries(data, list_check):
    matching_sublists = []
    list_check_lower = [check.lower() for check in list_check]

    for sublist in data:
        if len(sublist) >= 2 and isinstance(sublist[1], str):
            sublist_str_lower = sublist[1].lower()
            if any(check in sublist_str_lower for check in list_check_lower):
                matching_sublists.append(sublist)
                print(f"Match found: {sublist[1]} in {list_check}")

    for sublist in matching_sublists:
        data.remove(sublist)
    return data


def process_entries(match, tc_bounding_boxes):
    count_dict = {key: sum(entry[0] == key for entry in match) for key in tc_bounding_boxes}

    # Filter keys with occurrences greater than 1
    keys_to_process = [key for key, count in count_dict.items() if count > 1]

    closer_entries = []
    # Apply calculate_distance function to bounding boxes of selected keys
    for key in keys_to_process:
        entries = [entry for entry in match if entry[0] == key]
        for i in range(len(entries)):
            bbox1 = entries[i][2]
            bbox_tc = next(entry for entry in match if entry[0] == 'tc')
            distance = calculate_distance(bbox1, bbox_tc[2])
            closer_entries.append([key, i+1, distance, entries[i][1], entries[i][3]])

    # Create a dictionary to store the entry with the lowest number for each key
    lowest_entries = {}

    # Iterate through the data and update the lowest_entries dictionary
    for entry in closer_entries:
        key = entry[0]
        number = entry[1]
        distance = entry[2]
        value = entry[3]
        accuracy = entry[4]

        if key not in lowest_entries or number < lowest_entries[key][1]:
            lowest_entries[key] = [key, number, distance, value, accuracy]

        if key not in lowest_entries or accuracy > lowest_entries[key][4]:
            lowest_entries[key] = [key, number, distance, value, accuracy]

    # Convert the values of the dictionary to a list
    result_list = list(lowest_entries.values())

    return result_list


# Function to process the result list and add the final list
def add_results(match, result_list):
    count_dict = {}
    for item in match:
        key = item[0]
        count_dict[key] = count_dict.get(key, 0) + 1

    final_list = [item[0:2] for item in match if count_dict[item[0]] == 1]
    print(f"final_list {final_list}")
    final_list.extend([item[0], item[3]] for item in result_list)
    return final_list
