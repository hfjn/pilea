import logging
import sys
from builtins import property
from pathlib import Path
from typing import Tuple, Dict, Any, TYPE_CHECKING, Optional

import pendulum
import yaml

from pilea.resources.resource import Resource

logging.getLogger(__name__)

STUB_SEPARATOR = "<!-- stub -->"


class Post(Resource):
    def __init__(self, file: Path):
        super().__init__(file)
        self._config, self.content = self._parse_file_content(file.read_text())

        self.template = self._config.get("Template", "default")
        self.title = self._config.get("Title", "Untitled")

        self._date: pendulum.DateTime = pendulum.parse(self._config.get("Date", "1970-01-01"))

        self.stub = self._identify_or_extract_stub()

    @property
    def id(self):
        post_id = self._config.get("id", None)
        return post_id if post_id else self._construct_post_id()

    @property
    def extension(self):
        return "html"

    @property
    def draft(self):
        return self._config.get("Draft", False)

    def _construct_post_id(self):
        return f"{self.date}_{self.title.lower().replace(' ', '_')}"

    def _parse_file_content(self, content: str) -> Tuple[Dict[str, Any], str]:
        config, content = content.split("---", maxsplit=1)

        return yaml.safe_load(config), content

    def _identify_or_extract_stub(self) -> str:
        if STUB_SEPARATOR not in self.content:
            # TODO: Extract first x words as stub
            return ""
        stub, _ = self.content.split(STUB_SEPARATOR, maxsplit=1)
        return stub
