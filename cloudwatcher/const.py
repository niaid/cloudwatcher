METRIC_CMD = "metric"
LOG_CMD = "log"

SUBPARSER_MESSAGES = {
    METRIC_CMD: "Interact with AWS CloudWatch metrics.",
    LOG_CMD: "Interact with AWS CloudWatch logs.",
}

CLI_DEFAULTS = {
    "metric_name": "mem_used",
    "id": "provide_metric_id",
    "days": 1,
    "hours": 0,
    "minutes": 0,
    "unit": "Bytes",
    "stat": "Maximum",
    "period": 60,
    "dir": "./",
    "region": "us-east-1",
}
