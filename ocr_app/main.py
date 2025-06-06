import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
import cv2
from pdf2image import convert_from_bytes
from services.pipeline import DocumentPipeline
import easyocr
from fastapi.middleware.cors import CORSMiddleware

# Инициализация приложения и компонентов
app = FastAPI(
    title="OCR Microservice",
    description="API для обработки документов с использованием YOLOv8 и PaddleOCR",
    version="0.0.1"
)

origins = [
    "http://localhost",# Адрес вашего фронтенда
    "null"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация компонентов при старте
pipeline = DocumentPipeline()
reader = easyocr.Reader(['ru', 'en'])
# quality_checker = QualityAnalyzer()
# pdf_processor = PDFProcessor()


async def read_image(file: UploadFile) -> np.ndarray:
    """Чтение изображения из UploadFile"""
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


async def process_pdf(pdf_bytes: bytes) -> list:
    """Конвертация PDF в список изображений"""
    with tempfile.TemporaryDirectory() as temp_dir:
        images = convert_from_bytes(
            pdf_bytes,
            dpi=300,
            output_folder=temp_dir,
            fmt='jpeg'
        )
        return [cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR) for img in images]


@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Проверка работоспособности сервиса"""
    return {"status": "ok", "version": app.version}


@app.post("/process-document", tags=["Main"], summary="Полный пайплайн обработки")
async def process_document(
        file: UploadFile = File(..., description="Изображение или PDF-файл")
):
    """
    Основной эндпоинт для обработки документов:
    - Детекция документа
    - Коррекция перспективы
    - Проверка качества
    - OCR распознавание
    """
    try:
        # Определение типа контента
        is_pdf = file.filename.lower().endswith('.pdf')
        is_direct_ocr = file.filename.lower().endswith(('.png', '.jpeg', '.jpg'))

        # Обработка PDF
        if is_pdf:
            pdf_bytes = await file.read()
            images = await process_pdf(pdf_bytes)
            results = []
            for img in images:
                processed = await pipeline.process(img, is_uploaded_pdf=True)
                results.append(reader.readtext(processed[0], detail = 0, paragraph = True))
            # return {"results": results}
            return JSONResponse({
                "status": "success",
                "text": results,
                # "confidence": result["confidence"],
                "is_quality_ok": 'chert ego znaet'
            })

        # Обработка изображения
        image = await read_image(file)

        # Запуск полного пайплайна
        processed_images = await pipeline.process(image, is_uploaded_pdf=False)

        image_text = []

        for processed_image in processed_images:
            result = reader.readtext(processed_image, detail = 0, paragraph = True)
            image_text.extend(result)


        return JSONResponse({
            "status": "success",
            "text": image_text,
            # "confidence": result["confidence"],
            "is_quality_ok": 'chert ego znaet'
        })

    except Exception as e:
        raise HTTPException(500, f"Processing failed: {str(e)}")


@app.post("/detect-document", tags=["Utils"], summary="Только детекция документа")
async def detect_document(file: UploadFile = File(...)):
    """Эндпоинт только для детекции документа"""
    try:
        image = await read_image(file)
        doc_cnt, probes = pipeline.doc_detector.detect(image)
        if doc_cnt == 0:
            return {"document_detected": False}
        max_prob = probes[0] # i tak soydet
        return {
            "document_detected": True,
            "confidence": max_prob
        }
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/ocr", tags=["OCR"], summary="Только OCR распознавание")
async def direct_ocr(
        file: UploadFile = File(..., description="Изображение для прямого OCR")
):
    """Эндпоинт для OCR без предобработки"""
    try:
        image = await read_image(file)
        # bin = raw_to_binarized(image)
        result = reader.readtext(bin, detail = 0, paragraph = True)
        return {
            "text": result
        }
    except Exception as e:
        raise HTTPException(400, str(e))


# Middleware для ограничения размера файлов
@app.middleware("http")
async def limit_body_size(request, call_next):
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    content_length = request.headers.get('content-length')
    if content_length and int(content_length) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")
    return await call_next(request)


# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(
#         "main:app",
#         host="127.0.0.1",
#         port=8000,
#         reload=True,
#         # workers=2
#     )