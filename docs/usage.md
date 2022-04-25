The tool is highly configurable and can be used in a variety of ways. Naturally, the [metrics available to be monitored](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/metrics-collected-by-CloudWatch-agent.html) depend on the configuration of the CloudWatchAgent process.

By default the tool will report the `mem_used` metric starting 24 hours ago until present with granularity/period of 1 minute, expressed in Bytes.

Please refer to the usage below for more options:

```
usage: cloudwatcher [-h] [-jid JOB_ID] [-q QUERY_JSON] [-i ID] [-m METRIC] -iid
                     INSTANCE_ID [--uptime] [--days DAYS] [-hr HOURS] [-mi MINUTES]
                     [-u UNIT] [-s STAT] [-p PERIOD] [--save] [--plot] [-d DIR]
                     [--debug] [--namespace NAMESPACE]

CloudWatch metrics explorer. In order to use the tool a CloudWatchAgent process must
be running on the EC2 instance to be monitored.

optional arguments:
  -h, --help            show this help message and exit
  -jid JOB_ID, --job-id JOB_ID
                        Nephele job ID to use for the EC2 instance ID lookup. This
                        is not implemented yet.
  -q QUERY_JSON, --query-json QUERY_JSON
                        Path to a query JSON file. This is not implemented yet.
  -i ID, --id ID        The unique identifier to assign to the metric data. Must be
                        of the form '^[a-z][a-zA-Z0-9_]*$'.
  -iid INSTANCE_ID, --instance-id INSTANCE_ID
                        Instance ID, needs to follow 'i-<numbers>' format
  --uptime              Display the uptime of the instance in seconds. It's either
                        calculated precisely if the instance is still running, or
                        estimated based on the reported metrics.

 Options for metric collection start time:
  --days DAYS           How many days to subtract from the current date to determine
                        the metric collection start time (default: 1). Uptime will
                        be estimated in the timespan starting at least 15 ago.
  -hr HOURS, --hours HOURS
                        How many hours to subtract from the current time to
                        determine the metric collection start time (default: 0).
                        Uptime will be estimated in the timespan starting at least
                        15 ago.
  -mi MINUTES, --minutes MINUTES
                        How many minutes to subtract from the current time to
                        determine the metric collection start time (default: 0).
                        Uptime will be estimated in the timespan starting at least
                        15 ago.

 Options for metric measurement:
   --namespace NAMESPACE
                        Namespace to monitor the metrics within. This value must
                        match the 'Namespace' value in the config (default:
                        NepheleNamespace)
  -m METRIC, --metric METRIC
                        Name of the metric collected by CloudWatchAgent (default:
                        mem_used)
  -u UNIT, --unit UNIT  If you omit Unit then all data that was collected with any
                        unit is returned. If you specify a unit, it acts as a filter
                        and returns only data that was collected with that unit
                        specified. Use 'Bytes' for memory (default: Bytes)
  -s STAT, --stat STAT  The statistic to apply over the time intervals, e.g.
                        'Maximum' (default: Maximum)
  -p PERIOD, --period PERIOD
                        The granularity, in seconds, of the returned data points.
                        Choices: 1, 5, 10, 30, 60, or any multiple of 60 (default:
                        60)
  Output options:
  --save                Whether to store the response and metric data in JSON and
                        CSV files (default: False)
  --plot                Whether to plot the metric data (default: False)
  -d DIR, --dir DIR     Directory to store the results in. Used with `--save`
                        (default: ./)
  --debug               Whether debug mode should be launched (default: False)
```

### Minimal command

```console
python3.9 cloudwatch.py --instance-id i-024a73d6738255cbd
```

### Notes on metrics availabilty

Amazon CloudWatch retains metric data as follows:

- Data points with a period of less than 60 seconds are available for 3 hours.
- Data points with a period of 60 seconds (1-minute) are available for 15 days.
- Data points with a period of 300 seconds (5-minute) are available for 63 days.
- Data points with a period of 3600 seconds (1 hour) are available for 455 days (15 months).

Select your period of interest accordingly.
