""" Computing configuration representation """

import argparse

from ._version import __version__
from .const import LOG_CMD, METRIC_CMD, SUBPARSER_MESSAGES


class _VersionInHelpParser(argparse.ArgumentParser):
    def format_help(self):
        """Add version information to help text."""
        return (
            "version: {}\n".format(__version__)
            + super(_VersionInHelpParser, self).format_help()
        )


def build_argparser():
    """Build argument parser"""

    # args defaults
    metric_name = "mem_used"
    id = "memory_usage"
    days = 1
    hours = 0
    minutes = 0
    unit = "Bytes"
    stat = "Maximum"
    period = 60
    dir = "./"
    region = "us-east-1"

    # add argument parser
    parser = _VersionInHelpParser(description="CloudWatch logs and metrics explorer.")

    subparsers = parser.add_subparsers(dest="command")

    def add_subparser(cmd, msg, subparsers):
        return subparsers.add_parser(
            cmd,
            description=msg,
            help=msg,
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog, max_help_position=40, width=90
            ),
        )

    sps = {}
    for cmd, desc in SUBPARSER_MESSAGES.items():
        sps[cmd] = add_subparser(cmd, desc, subparsers)
        sps[cmd].add_argument(
            "--version",
            help="Print version and exit",
            action="version",
            version="%(prog)s {}".format(__version__),
        )
        sps[cmd].add_argument(
            "--debug",
            help="Whether debug mode should be launched (default: %(default)s)",
            action="store_true",
        )
        sps[cmd].add_argument(
            "--aws-region",
            help="Region to monitor the metrics within. (default: %(default)s)",
            type=str,
            required=False,
            default=region,
        )
        sps[cmd].add_argument(
            "--aws-access-key-id",
            help="AWS Access Key ID to use for authentication",
            type=str,
            required=False,
        )
        sps[cmd].add_argument(
            "--aws-secret-access-key",
            help="AWS Secret Access Key to use for authentication",
            type=str,
            required=False,
        )
        sps[cmd].add_argument(
            "--aws-session-token",
            help="AWS Session Token to use for authentication",
            type=str,
            required=False,
        )
        sps[cmd].add_argument(
            "--save",
            help="Whether to save the results to files in the selected directory (default: %(default)s)",
            action="store_true",
        )
        sps[cmd].add_argument(
            "-d",
            "--dir",
            help="Directory to store the results in. Used with `--save` (default: %(default)s)",
            default=dir,
        )

    sps[METRIC_CMD].add_argument(
        "-q",
        "--query-json",
        help="Path to a query JSON file. This is not implemented yet.",
        required=False,
        default=None,
    )
    sps[METRIC_CMD].add_argument(
        "-i",
        "--id",
        help="The unique identifier to assign to the metric data. Must be of the form '^[a-z][a-zA-Z0-9_]*$'.",
        default=id,
    )
    sps[METRIC_CMD].add_argument(
        "-m",
        "--metric",
        help="Name of the metric collected by CloudWatchAgent (default: %(default)s)",
        default=metric_name,
    )
    sps[METRIC_CMD].add_argument(
        "-iid",
        "--instance-id",
        help="Instance ID, needs to follow 'i-<numbers>' format",
        required=True,
        type=str,
    )
    sps[METRIC_CMD].add_argument(
        "--uptime",
        help="Display the uptime of the instance in seconds. It's either calculated precisely if the instance is still running, or estimated based on the reported metrics.",
        action="store_true",
    )
    sps[METRIC_CMD].add_argument(
        "--days",
        help="How many days to subtract from the current date to determine the metric collection start time (default: %(default)s). Uptime will be estimated in the timespan starting at least 15 ago.",
        default=days,
        type=int,
    )
    sps[METRIC_CMD].add_argument(
        "-hr",
        "--hours",
        help="How many hours to subtract from the current time to determine the metric collection start time (default: %(default)s). Uptime will be estimated in the timespan starting at least 15 ago.",
        default=hours,
        type=int,
    )
    sps[METRIC_CMD].add_argument(
        "-mi",
        "--minutes",
        help="How many minutes to subtract from the current time to determine the metric collection start time (default: %(default)s). Uptime will be estimated in the timespan starting at least 15 ago.",
        default=minutes,
        type=int,
    )
    sps[METRIC_CMD].add_argument(
        "-u",
        "--unit",
        help="""
            If you omit Unit then all data that was collected with any unit is returned.
            If you specify a unit, it acts as a filter and returns only data that was
            collected with that unit specified. Use 'Bytes' for memory (default: %(default)s)
            """,
        default=unit,
    )
    sps[METRIC_CMD].add_argument(
        "-s",
        "--stat",
        help="The statistic to apply over the time intervals, e.g. 'Maximum' (default: %(default)s)",
        default=stat,
    )
    sps[METRIC_CMD].add_argument(
        "-p",
        "--period",
        help="The granularity, in seconds, of the returned data points. Choices: 1, 5, 10, 30, 60, or any multiple of 60 (default: %(default)s)",
        default=period,
        type=int,
    )
    sps[METRIC_CMD].add_argument(
        "--plot",
        help="Whether to plot the metric data (default: %(default)s)",
        action="store_true",
    )
    sps[METRIC_CMD].add_argument(
        "--namespace",
        help="Namespace to monitor the metrics within. This value must match the 'Namespace' value in the CloudWatchAgent config (default: %(default)s)",
        type=str,
        required=True,
    )
    sps[LOG_CMD].add_argument(
        "-g",
        "--log-group-name",
        help="The log group name to monitor",
        required=True,
    )
    sps[LOG_CMD].add_argument(
        "-s",
        "--log-stream-name",
        help="The log stream name to monitor",
        required=True,
    )

    return parser
