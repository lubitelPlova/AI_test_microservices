from services.document_detector import DocumentDetector
from services.preprocessor import raw_photo_to_scan
import numpy as np

class DocumentPipeline:
    def __init__(self):
        self.doc_detector = DocumentDetector()

    async def process(
        self,
        image: np.ndarray,
        is_uploaded_pdf: bool
    ) -> list:
        # Пункт 2: Проверка качества для "хороших" документов
        document_cnt, probs = self.doc_detector.detect(image)
        if is_uploaded_pdf or document_cnt == 0:
            # bn = raw_to_binarized(image)
            return [image]

        # Пункт 3: Обработка фото со смартфона
        # 3.1: Детекция документа
        document_masks = self.doc_detector.segment(image)
        if not document_masks:
            raise ValueError("Документ не сегментирован")

        # 3.2: Перспективная коррекция
        scans = []
        for mask in document_masks:
            scan, _ = raw_photo_to_scan(mask, image)
            scans.append(scan)

        return scans