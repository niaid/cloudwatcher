import logging
import os
import sys

from rich.logging import RichHandler
from rich.console import Console
from pathlib import Path

from cloudwatcher.const import LOG_CMD, METRIC_CMD
from cloudwatcher.logwatcher import LogWatcher

from .argparser import build_argparser
from .metricwatcher import MetricWatcher
from .preset import get_metric_watcher_setup, PresetFilesInventory


def main():
    """
    Main entry point for the CLI.
    """
    parser = build_argparser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    logging.basicConfig(
        level="DEBUG" if args.debug else "INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
    _LOGGER = logging.getLogger(__name__)

    _LOGGER.debug(f"CLI arguments: {args}")

    if args.command == METRIC_CMD:

        if args.preset_list:
            Console().print(
                PresetFilesInventory(presets_dir=args.preset_dir).presets_table
            )
            sys.exit(0)

        if not os.path.exists(args.dir):
            _LOGGER.info(f"Creating directory: {args.dir}")
            os.makedirs(args.dir, exist_ok=True)

        mw_setup = get_metric_watcher_setup(namespace=args, presets_dir=args.preset_dir)
        metric_watcher = MetricWatcher(**mw_setup.to_dict())

        response = metric_watcher.query_ec2_metrics(
            days=args.days,
            hours=args.hours,
            minutes=args.minutes,
            stat=args.stat,
            period=args.period,
        )

        metric_watcher.log_response(response=response)
        metric_watcher.log_metric(response=response)
        metric_watcher.log_metric_summary(response=response)

        name_prefix = f"{metric_watcher.metric_id}_{metric_watcher.metric_name}"
        if args.save:
            metric_watcher.save_metric_json(
                file_path=os.path.join(args.dir, f"{name_prefix}.json"),
                response=response,
            )
            metric_watcher.save_metric_csv(
                file_path=os.path.join(args.dir, f"{name_prefix}.csv"),
                response=response,
            )
            metric_watcher.save_response_json(
                file_path=os.path.join(args.dir, f"{name_prefix}_response.json"),
                response=response,
            )

        if args.plot:
            metric_watcher.save_metric_plot(
                file_path=os.path.join(args.dir, f"{name_prefix}.png"),
                response=response,
            )

        if args.uptime:
            if not args.dimension_name == "InstanceId":
                _LOGGER.error(
                    "Uptime is only available for EC2 instances. "
                    "Please provide 'InstanceId' as dimension name and EC2 instance id"
                    " as the dimension value."
                )
                sys.exit(1)
            try:
                seconds_run = metric_watcher.get_ec2_uptime(
                    days=max(
                        15, args.days
                    ),  # metrics with a period of 60 seconds are available for 15 days
                    hours=args.hours,
                    minutes=args.minutes,
                    ec2_instance_id=args.dimension_value,
                )
                if seconds_run is not None:
                    _LOGGER.info(f"Instance uptime is {int(seconds_run)} seconds")
            except Exception as e:
                _LOGGER.warning(f"Failed to get instance uptime ({e})")

    if args.command == LOG_CMD:

        log_watcher = LogWatcher(
            log_group_name=args.log_group_name,
            log_stream_name=args.log_stream_name,
            aws_access_key_id=args.aws_access_key_id,
            aws_secret_access_key=args.aws_secret_access_key,
            aws_session_token=args.aws_session_token,
            aws_region_name=args.aws_region,
        )

        print(log_watcher.return_formatted_logs()[0])
        if args.save:
            log_watcher.save_log_file(
                file_path=os.path.join(
                    args.dir, f"{args.log_group_name}-{args.log_stream_name}.log"
                )
            )
