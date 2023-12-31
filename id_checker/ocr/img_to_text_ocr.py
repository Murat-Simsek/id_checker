import easyocr
from id_checker.utils.utils import resize_image


class OCRTranslat:
    def __init__(self, languages=['tr', 'en']):
        self.reader = easyocr.Reader(languages, gpu=True)

    def process_image(self, image_path, detail=10):
        image_resized = resize_image(image_path)
        result_ocr = self.reader.readtext(image_resized, detail=detail)
        return result_ocr
