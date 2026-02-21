"""PyInstaller hook for face_recognition_models."""
from PyInstaller.utils.hooks import get_module_file_attribute
import os

datas = []

try:
    import face_recognition_models
    models_path = os.path.dirname(face_recognition_models.__file__)
    datas.append((models_path, 'face_recognition_models'))
except ImportError:
    pass
