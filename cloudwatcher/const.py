METRIC_CMD = "metric"
LOG_CMD = "log"

SUBPARSER_MESSAGES = {
    METRIC_CMD: "Interact with AWS CloudWatch metrics.",
    LOG_CMD: "Interact with AWS CloudWatch logs.",
}
DEFAULT_QUERY_KWARGS = {
    "days": 1,
    "hours": 0,
    "minutes": 0,
    "stat": "Maximum",
    "period": 5,
}
QUERY_KWARGS_PRESETS = {
    "day": {"days": 1, "hours": 0, "minutes": 0, "stat": "Maximum", "period": 10},
    "hour": {"days": 0, "hours": 1, "minutes": 0, "stat": "Maximum", "period": 1},
    "minute": {"days": 0, "hours": 0, "minutes": 1, "stat": "Maximum", "period": 1},
}