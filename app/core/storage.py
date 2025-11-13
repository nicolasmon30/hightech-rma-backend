"""
Servicio de almacenamiento MinIO para adjuntos
"""
from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile, HTTPException, status
from io import BytesIO
from datetime import datetime
from typing import BinaryIO
import uuid
import os
from app.core.config import settings


# Inicializar cliente MinIO
def get_minio_client() -> Minio:
    """Obtener cliente MinIO configurado"""
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=False  # True si usas HTTPS
    )


def ensure_bucket_exists(bucket_name: str = settings.MINIO_BUCKET_NAME):
    """Crear bucket si no existe"""
    client = get_minio_client()
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"✅ Bucket '{bucket_name}' creado")
    except S3Error as e:
        print(f"❌ Error al crear bucket: {e}")
        raise


def validate_pdf_file(file: UploadFile) -> None:
    """Validar que sea PDF y no exceda 2MB"""
    # Validar extensión
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos PDF"
        )
    
    # Validar MIME type
    if file.content_type != 'application/pdf':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser un PDF válido"
        )
    
    # Validar tamaño (2MB)
    file.file.seek(0, 2)  # Ir al final
    file_size = file.file.tell()
    file.file.seek(0)  # Volver al inicio
    
    max_size = 2 * 1024 * 1024  # 2MB
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo excede el tamaño máximo de 2MB (tamaño: {file_size / 1024 / 1024:.2f}MB)"
        )


def generate_file_path(rma_id: int, original_filename: str) -> tuple[str, str]:
    """
    Generar path de almacenamiento: rmas/YYYY/MM/uuid_filename.pdf
    
    Returns:
        tuple: (stored_filename, full_path)
    """
    now = datetime.utcnow()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    
    # Generar nombre único
    ext = os.path.splitext(original_filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    
    # Path completo
    file_path = f"rmas/{year}/{month}/{unique_filename}"
    
    return unique_filename, file_path


async def upload_file_to_minio(
    file: UploadFile,
    rma_id: int,
    bucket_name: str = settings.MINIO_BUCKET_NAME
) -> dict:
    """
    Subir archivo a MinIO
    
    Returns:
        dict con: stored_filename, file_path, file_size, mime_type
    """
    # Validar archivo
    validate_pdf_file(file)
    
    # Generar path
    stored_filename, file_path = generate_file_path(rma_id, file.filename)
    
    # Obtener tamaño
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    # Subir a MinIO
    client = get_minio_client()
    ensure_bucket_exists(bucket_name)
    
    try:
        client.put_object(
            bucket_name=bucket_name,
            object_name=file_path,
            data=file.file,
            length=file_size,
            content_type=file.content_type
        )
        
        return {
            "stored_filename": stored_filename,
            "file_path": file_path,
            "file_size": file_size,
            "mime_type": file.content_type
        }
    
    except S3Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir archivo: {str(e)}"
        )


def download_file_from_minio(
    file_path: str,
    bucket_name: str = settings.MINIO_BUCKET_NAME
) -> BytesIO:
    """Descargar archivo desde MinIO"""
    client = get_minio_client()
    
    try:
        response = client.get_object(bucket_name, file_path)
        file_data = BytesIO(response.read())
        response.close()
        response.release_conn()
        return file_data
    
    except S3Error as e:
        if e.code == 'NoSuchKey':
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo no encontrado"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al descargar archivo: {str(e)}"
        )


def delete_file_from_minio(
    file_path: str,
    bucket_name: str = settings.MINIO_BUCKET_NAME
) -> None:
    """Eliminar archivo de MinIO"""
    client = get_minio_client()
    
    try:
        client.remove_object(bucket_name, file_path)
    except S3Error as e:
        # No lanzar error si el archivo no existe
        if e.code != 'NoSuchKey':
            print(f"⚠️ Error al eliminar archivo {file_path}: {e}")
