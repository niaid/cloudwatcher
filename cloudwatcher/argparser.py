""" Computing configuration representation """

import argparse

from cloudwatcher.const import CLI_DEFAULTS, LOG_CMD, METRIC_CMD, SUBPARSER_MESSAGES
from importlib.metadata import version

cloudwatcher_version = version("cloudwatcher")


class _VersionInHelpParser(argparse.ArgumentParser):
    def format_help(self):
        """Add version information to help text."""
        return (
            f"version: {cloudwatcher_version}\nDocumentation available at: "
            "https://niaid.github.io/cloudwatcher\n\n"
            + super(_VersionInHelpParser, self).format_help()
        )


def build_argparser():
    """Build argument parser"""

    # add argument parser
    parser = _VersionInHelpParser(
        description="CloudWatch logs and metrics explorer.",
    )

    subparsers = parser.add_subparsers(dest="command")

    def add_subparser(cmd, msg, subparsers):
        return subparsers.add_parser(
            cmd,
            description=msg,
            help=msg,
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog, max_help_position=30, width=150
            ),
        )

    sps = {}
    for cmd, desc in SUBPARSER_MESSAGES.items():
        sps[cmd] = add_subparser(cmd, desc, subparsers)
        sps[cmd].add_argument(
            "--version",
            help="Print version and exit",
            action="version",
            version=f"%(prog)s {cloudwatcher_version}",
        )
        sps[cmd].add_argument(
            "--debug",
            help="Whether debug mode should be launched (default: %(default)s)",
            action="store_true",
        )
        aws_creds_group = sps[cmd].add_argument_group(
            "AWS CREDENTIALS", "Can be ommited if set in environment variables"
        )
        aws_creds_group.add_argument(
            "--aws-region",
            help="Region to monitor the metrics within. (default: %(default)s)",
            type=str,
            required=False,
            default=CLI_DEFAULTS["region"],
            metavar="R",
        )
        aws_creds_group.add_argument(
            "--aws-access-key-id",
            help="AWS Access Key ID to use for authentication",
            type=str,
            required=False,
            metavar="K",
        )
        aws_creds_group.add_argument(
            "--aws-secret-access-key",
            help="AWS Secret Access Key to use for authentication",
            type=str,
            required=False,
            metavar="S",
        )
        aws_creds_group.add_argument(
            "--aws-session-token",
            help="AWS Session Token to use for authentication",
            type=str,
            required=False,
            metavar="T",
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
            default=CLI_DEFAULTS["dir"],
        )

    sps[METRIC_CMD].add_argument(
        "-i",
        "--id",
        help="The unique identifier to assign to the metric data. Must be of the form '^[a-z][a-zA-Z0-9_]*$'.",
        required=False,
        metavar="ID",
    )
    sps[METRIC_CMD].add_argument(
        "-m",
        "--metric",
        help="Name of the metric collected by CloudWatchAgent (default: %(default)s)",
        required=False,
        metavar="N",
    )
    sps[METRIC_CMD].add_argument(
        "--uptime",
        help="Display the uptime of the instance in seconds. It's either calculated precisely if the instance is still running, or estimated based on the reported metrics.",
        action="store_true",
    )
    metric_collection_start_time = sps[METRIC_CMD].add_argument_group(
        "METRIC COLLECTION TIME",
        "The time range to collect metrics from. Uptime will be estimated in the timespan starting at least 15 ago.",
    )
    metric_collection_start_time.add_argument(
        "--days",
        help="How many days to subtract from the current date to determine the metric collection start time (default: %(default)s).",
        default=CLI_DEFAULTS["days"],
        type=int,
        metavar="D",
    )
    metric_collection_start_time.add_argument(
        "-hr",
        "--hours",
        help="How many hours to subtract from the current time to determine the metric collection start time (default: %(default)s).",
        default=CLI_DEFAULTS["hours"],
        type=int,
        metavar="H",
    )
    metric_collection_start_time.add_argument(
        "-mi",
        "--minutes",
        help="How many minutes to subtract from the current time to determine the metric collection start time (default: %(default)s).",
        default=CLI_DEFAULTS["minutes"],
        type=int,
        metavar="M",
    )
    sps[METRIC_CMD].add_argument(
        "--dimensions",
        help="Elements of the dimensions list to use. Must be of the form: name1:value1 name2:value2",
        default=None,
        type=str,
        metavar="A",
        nargs="+",
    )
    preset = sps[METRIC_CMD].add_argument_group(
        "PRESETS", "Use one of the predefined presets to collect metrics."
    )
    preset.add_argument(
        "--preset-list",
        help="List all available presets.",
        action="store_true",
    )
    preset.add_argument(
        "--preset-dir",
        help="Path to the preset directory",
        default=None,
        type=str,
        metavar="D",
    )
    preset.add_argument(
        "--preset-name",
        help="Name of the preset to use.",
        default=None,
        type=str,
        metavar="N",
    )
    preset.add_argument(
        "--preset-path",
        help="Path to the preset file to use.",
        default=None,
        type=str,
        metavar="P",
    )

    sps[METRIC_CMD].add_argument(
        "-u",
        "--unit",
        help="""
            If you omit Unit then all data that was collected with any unit is returned.
            If you specify a unit, it acts as a filter and returns only data that was
            collected with that unit specified. Use 'Bytes' for memory (default: %(default)s)
            """,
        type=str,
        metavar="U",
    )
    sps[METRIC_CMD].add_argument(
        "-s",
        "--stat",
        help="The statistic to apply over the time intervals, e.g. 'Maximum' (default: %(default)s)",
        default=CLI_DEFAULTS["stat"],
        type=str,
        metavar="S",
    )
    sps[METRIC_CMD].add_argument(
        "-p",
        "--period",
        help="""
            The granularity, in seconds, of the returned data points. Choices: 1, 5, 10, 30, 60, or any multiple of 60 (default: %(default)s).
            It affects the data availability. See the docs 'Usage' section for more details.
            """,
        default=CLI_DEFAULTS["period"],
        type=int,
        metavar="P",
    )
    sps[METRIC_CMD].add_argument(
        "--plot",
        help="Whether to plot the metric data (default: %(default)s)",
        action="store_true",
    )
    sps[METRIC_CMD].add_argument(
        "--namespace",
        help="Namespace to monitor the metrics within. This value must match the 'Namespace' value in the CloudWatchAgent config.",
        type=str,
        metavar="N",
    )
    sps[LOG_CMD].add_argument(
        "-g",
        "--log-group-name",
        help="The log group name to monitor",
        required=True,
        type=str,
        metavar="G",
    )
    sps[LOG_CMD].add_argument(
        "-s",
        "--log-stream-name",
        help="The log stream name to monitor",
        required=True,
        type=str,
        metavar="S",
    )

    return parser
