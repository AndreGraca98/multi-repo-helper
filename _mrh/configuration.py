import json
from dataclasses import dataclass, field
from pathlib import Path

from .logger import get_logger

__all__ = ["Configuration", "ConfigurationReader", "DEFAULT_CONFIGURATION_READER"]

_log = get_logger(__name__)


@dataclass
class Configuration:
    filter: list[str] = field(default_factory=lambda: ["*"])  # all directories
    verbose: bool = False
    no_notify: bool = False
    pool_size: int = 10

    def to_dict(self) -> dict:
        return {
            "filter": self.filter,
            "verbose": self.verbose,
            "no_notify": self.no_notify,
            "pool_size": self.pool_size,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)

    def to_file(self, path: Path):
        assert path.suffix == ".json"
        if not path.is_file():
            path.touch(mode=0o644)  # rw-r--r--
        path.write_text(self.to_json())


class ConfigurationReader:
    """Reads a config file and returns a Configuration object."""

    __config: Configuration | None = None

    def __init__(self, path: Path) -> None:
        self.path = path

    def read(self) -> Configuration:
        if self.__config is not None:
            # Already read the cfg file
            return self.__config

        if not self.path.is_file():
            _log.debug(f"Config file {str(self.path)!r} not found")
            config = Configuration()
        elif self.path.read_text() == "":
            _log.warning(f"Config file {str(self.path)!r} is empty")
            config = Configuration()
        else:
            with open(self.path, "r") as f:
                _log.debug(f"Reading config file {str(self.path)!r}")
                config = Configuration(**json.load(f))

        self.__config = config
        return config


DEFAULT_CONFIGURATION_READER = ConfigurationReader(Path(".mrh.json").resolve())
