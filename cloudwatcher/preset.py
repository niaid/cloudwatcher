import os
import argparse
import logging
from typing import List, Dict, Union
from dataclasses import dataclass
from pydantic import BaseModel
from pathlib import Path
from rich.table import Table

from typing import List
import json

_LOGGER = logging.getLogger(__name__)


class PresetFilesInventory:
    def __init__(self, presets_dir: Union[Path, str] = None) -> None:
        """
        Initialize the preset inventory

        Args:
            presets_dir (Path): The path to the presets directory

        Raises:
            ValueError: If the presets directory does not exist
        """
        preset_dir = (
            Path(presets_dir)
            if presets_dir is not None
            else Path(__file__).parent / "presets"
        )
        if not preset_dir.exists():
            raise ValueError(f"Presets directory {preset_dir} does not exist")
        self._presets_dir = preset_dir
        _LOGGER.debug(f"Presets directory: {self.presets_dir}")
        self._presets = self._get_available_presets(self.presets_dir)

    def _get_available_presets(self, presets_dir: Path) -> List[str]:
        return {
            preset_file.stem: preset_file
            for preset_file in presets_dir.iterdir()
            if preset_file.is_file() and preset_file.suffix == ".json"
        }

    @property
    def presets_table(self) -> Table:
        """
        Get a rich table with the available presets

        Returns:
            Table: The rich table
        """
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name")
        table.add_column("Path", style="dim")
        for preset_name, preset_path in self.presets.items():
            table.add_row(preset_name, preset_path.as_posix())
        table.title = f"Presets available in: {self.presets_dir}"
        return table

    @property
    def presets(self) -> Dict[str, Path]:
        """
        Get the available presets

        Returns:
            Dict[str, Path]: The available presets
        """
        return self._presets

    @property
    def presets_list(self) -> List[str]:
        """
        Get the list of available presets

        Returns:
            List[str]: The list of available presets
        """
        return list(self._presets.keys())

    @property
    def presets_dir(self) -> Path:
        """
        Get the presets directory

        Returns:
            Path: The presets directory
        """
        return self._presets_dir

    def get_preset_path(self, preset_name: str) -> Path:
        """
        Get the preset file content

        Args:
            preset_name (str): The name of the preset

        Returns:
            Path: the path to the preset file
        """
        if preset_name not in self.presets:
            raise ValueError(
                f"Preset {preset_name} not found. Available presets: "
                f"{', '.join(self.presets.keys())}"
            )
        return self.presets[preset_name]


class Dimension(BaseModel):
    """
    A class for AWS CloudWatch dimension

    Args:
        Name (str): The name of the dimension
        Value (str): The value of the dimension
    """

    Name: str
    Value: str

    def __str__(self):
        return f"{self.Name}:{self.Value}"

    def __repr__(self):
        return self.__str__()


@dataclass
class MetricWatcherSetup:
    """
    A class for the setup of the MetricWatcher
    """

    namespace: str
    dimensions_list: List[Dimension]
    metric_name: str
    metric_id: str
    metric_unit: str
    aws_access_key_id: str = None
    aws_secret_access_key: str = None
    aws_session_token: str = None
    aws_region_name: str = None

    def __post_init__(self):
        self.aws_access_key_id = self.aws_access_key_id or os.environ.get(
            "AWS_ACCESS_KEY_ID"
        )
        self.aws_secret_access_key = self.aws_secret_access_key or os.environ.get(
            "AWS_SECRET_ACCESS_KEY"
        )
        self.aws_session_token = self.aws_session_token or os.environ.get(
            "AWS_SESSION_TOKEN"
        )
        self.aws_region_name = self.aws_region_name or os.environ.get(
            "AWS_DEFAULT_REGION"
        )
        self.dimensions_list = [
            Dimension(**dimension) for dimension in self.dimensions_list
        ]

    @classmethod
    def from_dict(cls, data: dict) -> "MetricWatcherSetup":
        """
        Create a MetricWatcherSetup object from a dictionary

        Args:
            data (dict): The dictionary to use
        """
        return cls(**data)

    @classmethod
    def from_json(cls, file_path: str) -> "MetricWatcherSetup":
        """
        Create a MetricWatcherSetup object from a JSON file

        Args:
            file_path (str): The path to the JSON file
        """
        with open(file_path) as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_dict(self) -> dict:
        """
        Convert the MetricWatcherSetup object to a dictionary

        Returns:
            dict: The dictionary representation of the object
        """
        return self.__dict__

    def upsert_dimensions(self, dimensions_specs: List[str] = None):
        """
        Upsert the dimensions list with the dimensions specified in the environment

        Args:
            dimensions_spec (List[str]): A list of strings in the format of "Name:Value"
        """
        if dimensions_specs is None:
            return
        for dimension_spec in dimensions_specs:
            name, value = dimension_spec.split(":")
            for dimension in self.dimensions_list:
                if dimension.Name == name:
                    dimension.Value = value
                    break
            else:
                self.dimensions_list.append(Dimension(Name=name, Value=value))


def get_metric_watcher_setup(
    namespace: argparse.Namespace, presets_dir: Path
) -> MetricWatcherSetup:
    """
    Get a MetricWatcherSetup object from a preset

    Args:
        namespace (argparse.Namespace): The namespace to use
        logger (Logger): The logger to use. Defaults to None
        presets_dir (Path): The path to the presets directory

    Returns:
        MetricWatcherSetup: The MetricWatcherSetup object
    """

    if namespace.preset_name is not None or namespace.preset_path is not None:
        if namespace.preset_path is not None:
            preset_path = Path(namespace.preset_path)
        else:
            presets_inventory = PresetFilesInventory(presets_dir)
            preset_path = presets_inventory.get_preset_path(namespace.preset_name)
        _LOGGER.info(f"Using preset: {preset_path}")
        mw_setup = MetricWatcherSetup.from_json(preset_path)
        mw_setup.namespace = namespace.namespace or mw_setup.namespace
        mw_setup.metric_name = namespace.metric or mw_setup.metric_name
        mw_setup.metric_id = namespace.id or mw_setup.metric_id
    else:
        mw_setup = MetricWatcherSetup(
            namespace=namespace.namespace,
            metric_name=namespace.metric,
            metric_id=namespace.id,
            metric_unit=namespace.unit,
            dimensions_list=[],
        )
    mw_setup.upsert_dimensions(namespace.dimensions)
    _LOGGER.debug(f"MetricWatcherSetup: {mw_setup}")
    return mw_setup
