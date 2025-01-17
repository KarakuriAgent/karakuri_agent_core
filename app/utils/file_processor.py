from fastapi import UploadFile, HTTPException
from typing import Optional, Tuple, Set
from PIL import Image
import io
import logging
from unstructured.partition.auto import partition
import tempfile
import os

logger = logging.getLogger(__name__)

# 画像として扱うMIMEタイプの定義
IMAGE_MIME_TYPES: Set[str] = {
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'image/bmp',
    'image/tiff',
    'image/svg+xml'
}

async def extract_text_from_file(file_content: bytes, filename: str) -> Optional[str]:
    """
    Extract text from various file formats.
    Supports PDF, DOCX, XLSX, etc.
    """
    try:
        with tempfile.NamedTemporaryFile(suffix=f"_{filename}", delete=False) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name

        elements = partition(filename=temp_path)
        text = "\n\n".join([str(el) for el in elements])

        os.unlink(temp_path)
        return text
    except Exception as e:
        logger.error(f"Error extracting text from file {filename}: {str(e)}")
        return None

async def process_uploaded_file(
    file: Optional[UploadFile]
) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Process uploaded file and return image content and extracted text.
    Returns (image_content, extracted_text)
    """
    if not file:
        return None, None

    content_type = file.content_type or ''
    file_content = await file.read()

    # MIMEタイプとファイル内容の検証
    if content_type in IMAGE_MIME_TYPES:
        try:
            # 実際に画像として開けるか確認
            Image.open(io.BytesIO(file_content))
            return file_content, None
        except Exception as e:
            logger.error(f"Invalid image file: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Invalid image file"
            )
    else:
        # その他のファイルとして処理
        try:
            extracted_text = await extract_text_from_file(file_content, file.filename)
            if extracted_text is None:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to extract text from file"
                )
            return None, extracted_text
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Error processing file: {str(e)}"
            )