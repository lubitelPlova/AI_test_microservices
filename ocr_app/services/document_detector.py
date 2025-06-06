from ultralytics import YOLO
import cv2
import numpy as np

class DocumentDetector:
    def __init__(self):
        self._model_seg = YOLO('./models/yolov8-doc-seg.pt')
        # self._model_clf = YOLO('yolov8n-cls.pt')

    def detect(self, image) -> int:
        """
        Метод определяет, количество документов на фото. Возвращает их количество
        """
        results = self._model_seg(image)[0]
        # print(results.probs)
        # classes_names = results.names
        classes = results.boxes.cls.cpu().numpy()
        probs = results.boxes.conf.cpu().numpy()


        return len(classes), probs
        
    def segment(self, image) -> list:
        """
        Метод определяет маску для каждого документа на фото. Возвращает массив масок.
        """
        orig = image.copy()
        h_or, w_or = image.shape[:2]
        image = cv2.resize(image, (640, 640))
        results = self._model_seg(image)[0]

        masks = results.masks.data.cpu().numpy()
        
        mask_arr = []
        # Наложение масок на изображение
        for _, mask in enumerate(masks):
            # Изменение размера маски перед созданием цветной маски
            mask_resized = cv2.resize(mask, (w_or, h_or))
            mask_resized = (mask_resized * 255).astype('uint8')
            mask_arr.append(mask_resized)

        return mask_arr

        
            