import os
from typing import List, Dict
from dataclasses import dataclass
from pydantic import BaseModel
from logging import Logger
from pathlib import Path

from typing import List
import json


class PresetFilesInventory:
    def __init__(self) -> None:
        self._presets = self._get_available_presets()

    def _get_available_presets(self) -> List[str]:
        return {
            preset_file.stem: preset_file
            for preset_file in (Path(__file__).parent / "presets").iterdir()
        }

    @property
    def presets(self) -> Dict[str, Path]:
        return self._presets

    def get_preset(self, preset_name: str) -> str:
        if preset_name not in self.presets:
            raise ValueError(
                f"Preset {preset_name} not found. Available presets: {self.presets}"
            )
        return self.presets[preset_name]


class Dimension(BaseModel):
    Name: str
    Value: str

    def __str__(self):
        return f"{self.Name}:{self.Value}"

    def __repr__(self):
        return self.__str__()


@dataclass
class MetricWatcherSetup:
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
    preset_name: str = None, preset_path: str = None, logger: Logger = None
) -> MetricWatcherSetup:
    """
    Get a MetricWatcherSetup object from a preset

    Args:
        preset_name (str): The name of the preset to use. Defaults to None
        preset_path (str): The path to the preset file. Defaults to None
        logger (Logger): The logger to use. Defaults to None

    Returns:
        MetricWatcherSetup: The MetricWatcherSetup object
    """
    if preset_name is None and preset_path is None:
        raise ValueError("Either preset_name or preset_path must be provided")

    if preset_path is None:
        preset_path = PresetFilesInventory().get_preset(preset_name)
    logger.info(f"Using preset: {preset_path}")
    return MetricWatcherSetup.from_json(preset_path)
