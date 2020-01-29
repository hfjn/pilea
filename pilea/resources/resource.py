from abc import abstractmethod, ABCMeta
from pathlib import Path

import pendulum


class Resource:
    def __init__(self, file: Path):
        self.file = file
        self._date = pendulum.now()

    @property
    def date(self):
        return self._date.to_date_string()

    @property
    def pretty_date(self):
        return self._date.format("%A %d %B %Y")

    @abstractmethod
    def extension(self):
        raise NotImplemented

    @abstractmethod
    def id(self):
        raise NotImplemented

    @property
    def target_name(self):
        return f"{self.id}.{self.extension}"
