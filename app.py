import os
import uuid
from flask import Flask, request
from werkzeug.utils import secure_filename
from id_checker.utils.image_rotation import ImageRotation
from id_checker.ocr.img_to_text_ocr import OCRTranslat
from id_checker.utils.utils import tc_bounding_boxes, id_back_boxes, list_check
from id_checker.yolo_v8.yoloV8 import ImageIdDetector
from id_checker.utils.utils import (filter_boxes,
                                    find_matching_text,
                                    convert_to_type,
                                    process_entries,
                                    add_results, remove_unwanted_entries)


ocr_translat = OCRTranslat()
image_detect = ImageIdDetector(model_path="id_checker/models/yolo_model/yolo_v8_id.pt")


app = Flask(__name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}


@app.route('/Idchecker', methods=['POST'])
def upload_and_process():
    # Check if the 'file' key exists in the request
    if 'file' not in request.files:
        return 'No file found', 400

    file = request.files['file']

    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        # Generate a random filename
        filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(file.filename)[1])
        print(filename)

        # Create the 'static' directory if it doesn't exist
        if not os.path.exists('static'):
            os.makedirs('static')

        # Save the file to the 'static' folder
        saved_image_path = os.path.join('static', filename)
        file.save(saved_image_path)

        class_img = image_detect.process_image(saved_image_path, save_dir="Saved_output/")

        return f'The image is: {class_img}'
    else:
        return 'Invalid file extension. Only JPG and PNG files are allowed.', 400


@app.route('/imageReader', methods=['POST'])
def image_reader():
    # Check if the 'file' key exists in the request
    if 'file' not in request.files:
        return 'No file found', 400

    file = request.files['file']

    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        # Generate a random filename
        filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(file.filename)[1])
        print(filename)

        # Create the 'static' directory if it doesn't exist
        if not os.path.exists('static'):
            os.makedirs('static')

        # Save the file to the 'static' folder
        saved_image_path = os.path.join('static', filename)
        file.save(saved_image_path)

        # Yolov8 image detection
        class_img = image_detect.process_image(saved_image_path, save_dir="Saved_output/")

        croped_image_path = os.path.join('Saved_output/output_image', "croped_img" + ".jpg")

        if "front" in class_img:
            dict_boxes = tc_bounding_boxes
        elif "back" in class_img:
            dict_boxes = id_back_boxes
        else:
            return 'The image was not recognised as front or back TC id.', 400

        # TODO: Add rotation of image here
        saved_image_path_rotated = os.path.join('static', "rotated" + filename)
        image_rotate = ImageRotation()
        image_rotate.process_image(croped_image_path, saved_image_path_rotated)

        # OCR
        ocr_results = ocr_translat.process_image(saved_image_path_rotated)
        ocr_all = []
        for t in ocr_results:
            ocr_all.append(t)
        filter_boxes_results = filter_boxes(ocr_all, min_text_confidence=45)

        extracted_text = find_matching_text(filter_boxes_results, dict_boxes)

        # Iterate through the data and update the second element using the convert_to_type function to change the type
        for item in extracted_text:
            item[1] = convert_to_type(item[1])
        # Filter out the items that are not of desired type
        extracted_text = [item for item in extracted_text if type(item[1]) == item[4]]

        extracted_text = remove_unwanted_entries(extracted_text, list_check)
        # Process the entries and remove duplicates according to the tc_bounding_boxes and distances of tc bboxes
        final_results = process_entries(extracted_text, dict_boxes)
        print(final_results)
        final_results_send = add_results(extracted_text, final_results)
        return f'Extracted information from image: {final_results_send}'
    else:
        return 'Invalid file extension. Only JPG and PNG files are allowed.', 400


if __name__ == '__main__':
    app.run(debug=True)
