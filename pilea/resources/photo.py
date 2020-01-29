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

        self._date: DateTime = pendulum.parse(self._exif.get("DateTime", "1970-1-1"))

        self._height = self._image.height
        self._width = self._image.width

    @property
    def extension(self):
        return "jpeg"

    @property
    def id(self):
        return self._date.to_iso8601_string()

    def scale(self) -> None:
        self._image = Image.open(self.file)
        if self._height <= MAX_HEIGHT and self._width <= MAX_WIDTH:
            return None
        elif self._height >= self._width:
            width = int(MAX_HEIGHT / self._height * self._width)
            self._image = self._image.resize((width, MAX_HEIGHT))
        else:
            height = int(MAX_WIDTH / self._width * self._height)
            self._image = self._image.resize((height, MAX_HEIGHT), Image.ANTIALIAS)

    def save(self, path: Path):
        self._image.save(path / self.target_name)
