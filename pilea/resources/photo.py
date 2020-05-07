from pathlib import Path
from typing import TYPE_CHECKING, Dict

from PIL import Image
from PIL.ExifTags import TAGS
import pendulum
from pendulum import DateTime

from pilea.resources.resource import Resource

MAX_HEIGHT = MAX_WIDTH = 1500


class Photo(Resource):
    def __init__(self, file: Path):
        super().__init__(file)

        self._image: Image.Image = Image.open(file)
        self._image.verify()

        self._exif: Dict[str, str] = {
            TAGS.get(exif_key): exif_value for exif_key, exif_value in self._image._getexif().items()
        }

        self._date: DateTime = pendulum.parse(self._exif.get("DateTimeOriginal", None))
        if not self._date:
            self._date = pendulum.parse(self._exif.get("DateTime", "1970-1-1"))

        self._height = self._image.height
        self._width = self._image.width

    @property
    def extension(self):
        return "jpg"

    @property
    def id(self):
        return self._date.to_iso8601_string()

    def save(self, path: Path):
        # TODO: Set Copyright in exif
        self._image: Image.Image = Image.open(self.file)

        if self._exif.get("Orientation") == 3:
            self._image = self._image.rotate(180, expand=True)
        elif self._exif.get("Orientation") == 6:
            self._image = self._image.rotate(270, expand=True)
        elif self._exif.get("Orientation") == 9:
            self._image = self._image.rotate(90, expand=True)

        self._image.thumbnail((MAX_WIDTH, MAX_HEIGHT))

        self._image.save(path / self.target_name)
