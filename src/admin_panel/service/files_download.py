# stdlib
import os
import shutil

# thirdparty
from fastapi import UploadFile

# project
from common.utils import generate_random_string


def download_images(form_images: list[UploadFile]) -> list[str]:
    """Загрузка файлов в хранилище и формирование списка путей в новой директории"""

    result = []

    images_path = os.environ.get("IMAGES_PATH")

    if not images_path:
        raise EnvironmentError

    for file in form_images:
        try:
            ext = file.filename.split(".")[-1]
            new_name = generate_random_string() + "." + ext
            new_file_path = os.path.join(images_path, new_name)

            with open(new_file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
                result.append(new_file_path)

        except Exception:
            continue
        finally:
            file.file.close()

    return result
