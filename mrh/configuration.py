import json
from dataclasses import dataclass, field
from pathlib import Path

from mrh.logger import get_logger

__all__ = ["Configuration", "ConfigurationReader", "DEFAULT_CONFIGURATION"]

_log = get_logger(__name__)


@dataclass
class Configuration:
    filter: list[str] = field(default_factory=list)
    verbose: bool = False
    no_notify: bool = False


@dataclass
class ConfigurationReader:
    """Reads a config file and returns a Configuration object."""

    path: Path

    def read(self) -> Configuration:
        if not self.path.is_file():
            _log.warning(f"Config file {str(self.path)!r} not found")
            return Configuration()

        if self.path.read_text() == "":
            _log.warning(f"Config file {str(self.path)!r} is empty")
            return Configuration()

        with open(self.path, "r") as f:
            _log.debug(f"Reading config file {str(self.path)!r}")
            return Configuration(**json.load(f))


DEFAULT_CONFIGURATION = ConfigurationReader(Path(".mrh.json").resolve()).read()
