from ultralytics import YOLO
from PIL import Image
import cv2
import json
import os
from shutil import move


class ImageIdDetector:
    def __init__(self, model_path='id_checker/id_checker/models/yolo_model/yolo_v8_id.pt'):
        self.model = YOLO(model_path)

    def process_image(self, image_path, save_dir="Saved_output/"):
        results = self.model.predict(source=image_path)

        for r in results:
            r.save_crop(save_dir=save_dir, file_name="croped_img")

            id_folder = os.path.join(save_dir, "id")
            back_folder = os.path.join(save_dir, "back")
            front_folder = os.path.join(save_dir, "front")

            destination_folder = os.path.join(save_dir, "output_image")

            self.move_and_delete_images(id_folder, destination_folder, back_folder, front_folder)

            # Json of data results
            r_json = r.tojson()
            parsed_data = json.loads(r_json)
            class_of_image = []

            # Extract and print the 'name' values
            for item in parsed_data:
                name_value = item.get('name')
                if name_value is not None:
                    class_of_image.append(name_value)

        return class_of_image

    @staticmethod
    def move_and_delete_images(source_folder, destination_folder, back_folder, front_folder):
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        for filename in os.listdir(source_folder):
            source_path = os.path.join(source_folder, filename)
            destination_path = os.path.join(destination_folder, filename)
            move(source_path, destination_path)
            # remove the files in front and back folders.
            back_file = os.path.join(back_folder, filename)
            front_file = os.path.join(front_folder, filename)
            if os.path.exists(back_file):
                os.remove(back_file)
            if os.path.exists(front_file):
                os.remove(front_file)
