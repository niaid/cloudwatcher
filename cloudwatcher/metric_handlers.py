import csv
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple

import matplotlib.pyplot as plt
import pytz
from rich.console import Console
from rich.table import Table

_LOGGER = logging.getLogger(__name__)


def convert_mem(value: int, force_suffix: str = None) -> Tuple[float, str]:
    """
    Convert memory in bytes to the highest possible, or desired memory unit

    Args:
        value (int): The memory in bytes
        force_suffix (str): The desired memory unit

    Returns:
        Tuple[float, str]: The memory in the desired unit and the unit
    """
    suffixes = ["B", "KB", "MB", "GB", "TB"]
    if force_suffix is not None:
        try:
            idx = suffixes.index(force_suffix)
        except ValueError:
            raise ValueError(f"Forced memory unit must me one of: {suffixes}")
        else:
            return value / float(pow(1024, idx)), force_suffix
    suffixIndex = 0
    while value > 1024 and suffixIndex < len(suffixes) - 1:
        suffixIndex += 1
        value = value / 1024.0
    return value, suffixes[suffixIndex]


@dataclass
class TimedMetric:
    """
    Timed metric object

    Args:
        timestamps (List[datetime]): The timestamps of the metric
        values (List[float]): The values of the metric
        label (str): The label of the metric
    """

    label: str
    timestamps: List[datetime]
    values: List[str]

    def __len__(self):
        if len(self.timestamps) == len(self.values):
            return len(self.values)
        raise ValueError("The internal timed metric lengths are not equal")


class Handler(ABC):
    """
    Abstract class to establish the interface for data handling
    """

    @abstractmethod
    def __init__(self, response: dict, logger: logging.Logger) -> None:
        """
        Initialize the handler

        Args:
            response (dict): The response from the AWS API
            logger (logging.Logger): The logger to use
        """
        pass

    @abstractmethod
    def __call__(self, target: str) -> None:
        """
        Execute the handler

        Args:
            target (str): The target to use for the handler
        """
        pass


class ResponseHandler(Handler):
    """
    Abstract class to establish the interface for a response handling
    """

    def __init__(self, response: dict) -> None:
        """
        Initialize the handler

        Args:
            response (dict): The response from the AWS API
        """
        self.response = response


class TimedMetricHandler(Handler):
    """
    Class to establish the interface for a timed metric handling
    """

    def __init__(self, timed_metric: TimedMetric) -> None:
        """
        Initialize the handler

        Args:
            timed_metric (TimedMetric): The timed metric to use
        """
        self.timed_metric = timed_metric


class ResponseSaver(ResponseHandler):
    """
    Save the response to a file
    """

    def __call__(self, target: str) -> None:
        """
        Save the response to a file

        Args:
            target (str): The target file to save the response to
        """
        with open(target, "w") as f:
            json.dump(self.response, f, indent=4, default=str)
        _LOGGER.info(f"Saved response to: {target}")


class ResponseLogger(ResponseHandler):
    """
    Log the response to the console
    """

    def __call__(self, target: str) -> None:
        if target is not None:
            raise NotImplementedError(
                "Logging responses to a file is not yet implemented."
            )
        _LOGGER.debug(json.dumps(self.response, indent=4, default=str))


class TimedMetricPlotter(TimedMetricHandler):
    def __call__(self, target: str, metric_unit: str) -> None:
        """
        Plot the timed metric

        Args:
            target (str): The target file to save the plot to
            metric_unit (str): The unit of the metric
        """
        values = self.timed_metric.values
        if self.timed_metric.label.startswith("mem") and metric_unit == "Bytes":
            metric_unit = "GB"
            values = [convert_mem(v, force_suffix=metric_unit)[0] for v in values]
        plt.plot(
            self.timed_metric.timestamps,
            values,
            linewidth=0.8,
        )
        plt.title(
            f"{self.timed_metric.label} over time",
            loc="right",
            fontstyle="italic",
        )
        plt.ylabel(f"{self.timed_metric.label} ({metric_unit})")
        plt.ticklabel_format(axis="y", style="plain", useOffset=False)
        plt.tick_params(left=True, bottom=False, labelleft=True, labelbottom=False)
        plt.savefig(
            target,
            bbox_inches="tight",
            pad_inches=0.1,
            dpi=300,
            format="png",
        )
        _LOGGER.info(f"Saved '{self.timed_metric.label}' plot to: {target}")


class TimedMetricSummarizer(TimedMetricHandler):
    def __call__(
        self,
        target: str,
        metric_unit: str,
        summarizer: Tuple[str, callable],
    ) -> None:
        """
        Summarize the metric

        Args:
            target (str): The target file to save the summary to
            metric_unit (str): The unit of the metric
            summarizer (Tuple[str, callable]): The summarizer to use and the function to use
        """
        if target is not None:
            raise NotImplementedError("Logging to a file is not yet implemented.")
        timespan = self.timed_metric.timestamps[0] - self.timed_metric.timestamps[-1]
        _LOGGER.info(
            f"Retrieved '{self.timed_metric.label}' {len(self.timed_metric.values)} "
            f"measurements over {timespan} timespan"
        )
        summary = summarizer[1](self.timed_metric.values)
        if self.timed_metric.label.startswith("mem") and metric_unit == "Bytes":
            mem, metric_unit = convert_mem(summary)
            _LOGGER.info(
                f"{summarizer[0]} '{self.timed_metric.label}' is "
                f"{mem:.2f} {metric_unit} over {timespan} timespan"
            )
        else:
            _LOGGER.info(
                f"{summarizer[0]} '{self.timed_metric.label}' is "
                f"{summary} over {timespan} timespan"
            )


class TimedMetricLogger(TimedMetricHandler):
    def __call__(self, target: str) -> None:
        """
        Log the timed metric as a table
        """
        if target is not None:
            raise NotImplementedError("Logging to a file is not yet implemented.")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column(f"Time ({str(pytz.utc)})", style="dim", justify="center")
        table.add_column("Value")
        values = [
            self.mem_to_str(v) if self.timed_metric.label.startswith("mem") else str(v)
            for v in self.timed_metric.values
        ]
        for i in range(len(self.timed_metric.timestamps)):
            table.add_row(
                self.timed_metric.timestamps[i].strftime("%H:%M:%S"), values[i]
            )
        console = Console()
        console.print(table)

    @staticmethod
    def mem_to_str(size: int, precision: int = 3) -> str:
        """
        Convert bytes to human readable string

        Args:
            size (int): The size in bytes
            precision (int): The precision to use, number of decimal places

        Returns:
            str: The human readable string
        """
        size, suffix = convert_mem(size)
        return "%.*f %s" % (precision, size, suffix)


class TimedMetricJsonSaver(TimedMetricHandler):
    def __call__(self, target: str) -> None:
        """
        Write the object to a json file

        Args:
            target (str): The target file to save the object to
        """
        with open(target, "w") as f:
            json.dump(
                {
                    "Label": self.timed_metric.label,
                    "Timestamps": self.timed_metric.timestamps,
                    "Values": self.timed_metric.values,
                },
                f,
                indent=4,
                default=str,
            )
        _LOGGER.info(f"Saved '{self.timed_metric.label}' data to: {target}")


class TimedMetricCsvSaver(TimedMetricHandler):
    def __call__(self, target: str) -> None:
        """
        Write the object to a csv file

        Args:
            target (str): The target file to save the object to
        """
        with open(target, "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)

            # write the header
            writer.writerow(["time", "value"])
            # write the data
            for i in range(len(self.timed_metric)):
                writer.writerow(
                    [self.timed_metric.timestamps[i], self.timed_metric.values[i]]
                )
        _LOGGER.info(f"Saved '{self.timed_metric.label}' data to: {target}")
