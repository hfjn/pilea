import logging
import sys
from builtins import property
from pathlib import Path
from typing import Tuple, Dict, Any, TYPE_CHECKING, Optional

import pendulum
import yaml

if TYPE_CHECKING:
    from pilea.state import State


logging.getLogger(__name__)

STUB_SEPARATOR = "<!-- stub -->"


class Post:
    def __init__(self, state: "State", file: Path):
        self._config, self.content = self._parse_file_content(file.read_text())
        self.stub = self._identify_or_extract_stub()
        self._state: "State" = state
        self.template = self._config.get("Template", "default")
        self.title = self._config.get("Title", "Untitled")

        self._date: pendulum.DateTime = pendulum.parse(
            self._config.get("Date", "1970-01-01")
        )
        self.file = file

    @property
    def id(self):
        post_id = self._config.get("id", None)
        return post_id if post_id else self._construct_post_id()

    @property
    def date(self):
        return self._date.to_date_string()

    @property
    def pretty_date(self):
        return self._date.format('%A %d %B %Y')

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

    @property
    def url(self):
        post_url: Optional[str] = self._config.get("url", None)
        if post_url:
            if post_url.startswith("/"):
                return post_url
            else:
                logging.error(f"{post_url} isn't a relative url /")
                sys.exit(1)
        base_path = self._state.extract_relative_file_path(self.file)
        return f"/{base_path.parent}/{self.id}.html"
