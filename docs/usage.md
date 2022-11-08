There are two modes of operation on the CLI:

- [`cloudwatcher metric`](#cloudwatch-metrics-monitoring)
- [`cloudwatcher log`](#cloudwatch-logs-monitoring)

```
cloudwatcher --help
```

```
Documentation available at: https://niaid.github.io/cloudwatcher

usage: cloudwatcher [-h] {metric,log} ...

CloudWatch logs and metrics explorer.

positional arguments:
  {metric,log}
    metric      Interact with AWS CloudWatch metrics.
    log         Interact with AWS CloudWatch logs.

optional arguments:
  -h, --help    show this help message and exit
```

## CloudWatch metrics monitoring

The tool is highly configurable and can be used in a variety of ways. Naturally, the [metrics available to be monitored](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/metrics-collected-by-CloudWatch-agent.html) depend on the configuration of the CloudWatchAgent process.

By default the tool will report the `mem_used` metric starting 24 hours ago until present with granularity/period of 1 minute, expressed in Bytes.

Please refer to the usage below for more options:

```
clouwatcher metric --help
```

```
Documentation available at: https://niaid.github.io/cloudwatcher

usage: cloudwatcher metric [-h] [--version] [--debug] [--aws-region R] [--aws-access-key-id K] [--aws-secret-access-key S] [--aws-session-token T]
                           [--save] [-d DIR] [-q Q] [-i ID] [-m N] [-dn N] -dv V [--uptime] [--days D] [-hr H] [-mi M] [-u U] [-s S] [-p P] [--plot]
                           --namespace N

Interact with AWS CloudWatch metrics.

optional arguments:
  -h, --help                  show this help message and exit
  --version                   Print version and exit
  --debug                     Whether debug mode should be launched (default: False)
  --save                      Whether to save the results to files in the selected directory (default: False)
  -d DIR, --dir DIR           Directory to store the results in. Used with `--save` (default: ./)
  -q Q, --query-json Q        Path to a query JSON file. This is not implemented yet.
  -i ID, --id ID              The unique identifier to assign to the metric data. Must be of the form '^[a-z][a-zA-Z0-9_]*$'.
  -m N, --metric N            Name of the metric collected by CloudWatchAgent (default: mem_used)
  -dn N, --dimension-name N   The name of the dimension to query. (default: InstanceId)
  -dv V, --dimension-value V  The value of the dimension to filter on.
  --uptime                    Display the uptime of the instance in seconds. It's either calculated precisely if the instance is still running, or
                              estimated based on the reported metrics.
  -u U, --unit U              If you omit Unit then all data that was collected with any unit is returned. If you specify a unit, it acts as a filter
                              and returns only data that was collected with that unit specified. Use 'Bytes' for memory (default: None)
  -s S, --stat S              The statistic to apply over the time intervals, e.g. 'Maximum' (default: Maximum)
  -p P, --period P            The granularity, in seconds, of the returned data points. Choices: 1, 5, 10, 30, 60, or any multiple of 60 (default:
                              60). It affects the data availability. See the docs 'Usage' section for more details.
  --plot                      Whether to plot the metric data (default: False)
  --namespace N               Namespace to monitor the metrics within. This value must match the 'Namespace' value in the CloudWatchAgent config.

AWS CREDENTIALS:
  Can be ommited if set in environment variables

  --aws-region R              Region to monitor the metrics within. (default: us-east-1)
  --aws-access-key-id K       AWS Access Key ID to use for authentication
  --aws-secret-access-key S   AWS Secret Access Key to use for authentication
  --aws-session-token T       AWS Session Token to use for authentication

METRIC COLLECTION TIME:
  The time range to collect metrics from. Uptime will be estimated in the timespan starting at least 15 ago.

  --days D                    How many days to subtract from the current date to determine the metric collection start time (default: 1).
  -hr H, --hours H            How many hours to subtract from the current time to determine the metric collection start time (default: 0).
  -mi M, --minutes M          How many minutes to subtract from the current time to determine the metric collection start time (default: 0).
```

### Command example

This minimal command will query dimesion `InstanceId` for `mem_used` in `Bytes` with period 60s over last 2 days.

```console
cloudwatcher metric --dimensions InstanceId:i-0e0165b35c8d648c8 --namespace NepheleNamespaceEC2 --metric mem_used --id mem_used --days 2 --stat Maximum --unit Bytes
```

### Notes on metrics availabilty

Amazon CloudWatch retains metric data as follows:

- Data points with a period of less than 60 seconds are available for 3 hours.
- Data points with a period of 60 seconds (1-minute) are available for 15 days.
- Data points with a period of 300 seconds (5-minute) are available for 63 days.
- Data points with a period of 3600 seconds (1 hour) are available for 455 days (15 months).

Select your period of interest accordingly. This is crucial as for example if the EC2 instance has stopped over 3 hours ago, selecting a < 60 second period will return an empty reponse.

### Using presets

As you can see, the command required to retrieve the metrics is quite long. To make it easier to use, you can create a preset file and use it to query the metrics. Alternatively, you can use one of the built-in presets.

List presets with:

```console
cloudwatcher metric --preset-list
```

Query metrics with preset:

```
cloudwatcher metric --preset <preset_name>
```

## CloudWatch logs monitoring

```
clouwatcher log --help
```

```
Documentation available at: https://niaid.github.io/cloudwatcher

usage: cloudwatcher log [-h] [--version] [--debug] [--aws-region R] [--aws-access-key-id K] [--aws-secret-access-key S] [--aws-session-token T]
                        [--save] [-d DIR] -g G -s S

Interact with AWS CloudWatch logs.

optional arguments:
  -h, --help                 show this help message and exit
  --version                  Print version and exit
  --debug                    Whether debug mode should be launched (default: False)
  --save                     Whether to save the results to files in the selected directory (default: False)
  -d DIR, --dir DIR          Directory to store the results in. Used with `--save` (default: ./)
  -g G, --log-group-name G   The log group name to monitor
  -s S, --log-stream-name S  The log stream name to monitor

AWS CREDENTIALS:
  Can be ommited if set in environment variables

  --aws-region R             Region to monitor the metrics within. (default: us-east-1)
  --aws-access-key-id K      AWS Access Key ID to use for authentication
  --aws-secret-access-key S  AWS Secret Access Key to use for authentication
  --aws-session-token T      AWS Session Token to use for authentication
```
