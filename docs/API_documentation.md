<script>
document.addEventListener('DOMContentLoaded', (event) => {
  document.querySelectorAll('h3 code').forEach((block) => {
    hljs.highlightBlock(block);
  });
});
</script>

<style>
h3 .content { 
    padding-left: 22px;
    text-indent: -15px;
 }
h3 .hljs .content {
    padding-left: 20px;
    margin-left: 0px;
    text-indent: -15px;
    martin-bottom: 0px;
}
h4 .content, table .content, p .content, li .content { margin-left: 30px; }
h4 .content { 
    font-style: italic;
    font-size: 1em;
    margin-bottom: 0px;
}

</style>

# Package `cloudwatcher` Documentation

## <a name="CloudWatcher"></a> Class `CloudWatcher`

A base class for CloudWatch managers

```python
def __init__(self, service_name: str, aws_region_name: Union[str, NoneType]=None, aws_access_key_id: Union[str, NoneType]=None, aws_secret_access_key: Union[str, NoneType]=None, aws_session_token: Union[str, NoneType]=None) -> None
```

Initialize CloudWatcher

#### Parameters:

- `service_name` (`str`): The name of the service
- `region_name` (`str`): The name of the region. Defaults to 'us-east-1'
- `aws_access_key_id` (`Optional[str]`): The AWS access key ID
- `aws_secret_access_key` (`Optional[str]`): The AWS secret access key
- `aws_session_token` (`Optional[str]`): The AWS session token

## <a name="MetricWatcher"></a> Class `MetricWatcher`

A class for AWS CloudWatch metric retrieval and parsing

```python
def __init__(self, namespace: str, dimension_name: str, dimension_value: str, metric_name: str, metric_id: str, metric_unit: Union[str, NoneType]=None, aws_access_key_id: Union[str, NoneType]=None, aws_secret_access_key: Union[str, NoneType]=None, aws_session_token: Union[str, NoneType]=None, aws_region_name: Union[str, NoneType]=None) -> None
```

Initialize MetricWatcher

#### Parameters:

- `namespace` (`str`): The namespace of the metric
- `region_name` (`Optional[str]`): The name of the region. Defaults to 'us-east-1'
- `start_token` (`Optional[str]`): The start token to use for the query

```python
def get_ec2_uptime(self, ec2_instance_id: str, days: int, hours: int, minutes: int) -> int
```

Get the runtime of an EC2 instance

#### Parameters:

- `days` (`int`): how many days to subtract from the current date to determine the metric collection start time
- `hours` (`int`): how many hours to subtract from the current time to determine the metric collection start time
- `minute` (`int`): how many minutes to subtract from the current time to determine the metric collection start time
- `ec2_instance_id` (`str`): the ID of the EC2 instance to queryReturns: int: runtime of the instance in seconds

```python
def is_ec2_running(self, ec2_instance_id: str) -> bool
```

Check if EC2 instance is running

#### Parameters:

- `ec2_instance_id` (`str`): the ID of the EC2 instance to query

#### Returns:

- `bool`: True if instance is running, False otherwise

```python
def log_metric(self, response: Union[Dict, NoneType]=None, query_preset: Union[str, NoneType]=None)
```

Query and log the metric data

#### Parameters:

- `kwargs` (``): keyword arguments to pass to the handler
- `response` (`dict`): response retrieved with `query_ec2_metrics`.A query is performed if not provided.
- `response` (`dict`): response from `query_ec2_metrics` method
- `query_kwargs` (`dict`): kwargs to pass to the EC2 query
- `query_preset` (`str`): period preset to use for the EC2 query

```python
def log_metric_summary(self, response: Union[Dict, NoneType]=None, query_preset: Union[str, NoneType]=None)
```

Query and summarize the metric data to a JSON file

#### Parameters:

- `file_path` (`str`): path to the file to save the metric data to
- `response` (`dict`): response retrieved with `query_ec2_metrics`.A query is performed if not provided.
- `response` (`dict`): response from `query_ec2_metrics` method
- `query_kwargs` (`dict`): kwargs to pass to the EC2 query
- `query_preset` (`str`): period preset to use for the EC2 query

```python
def log_response(self, response: Union[Dict, NoneType]=None, query_preset: Union[str, NoneType]=None)
```

Query and log the response

#### Parameters:

- `response` (`dict`): response retrieved with `query_ec2_metrics`.A query is performed if not provided.
- `response` (`dict`): response from `query_ec2_metrics` method
- `query_kwargs` (`dict`): kwargs to pass to the EC2 query
- `query_preset` (`str`): period preset to use for the EC2 query

```python
def query_ec2_metrics(self, days: int, hours: int, minutes: int, stat: str, period: int) -> Dict
```

Query EC2 metrics

#### Parameters:

- `namespace` (`str`): namespace to monitor the metrics within. This value must match the 'Nampespace' value in the config
- `days` (`int`): how many days to subtract from the current date to determine the metric collection start time
- `hours` (`int`): how many hours to subtract from the current time to determine the metric collection start time
- `minute` (`int`): how many minutes to subtract from the current time to determine the metric collection start time
- `stat` (`str`): stat to use, e.g. 'Maximum'
- `period` (`int`): the granularity, in seconds, of the returned data pointsreturn dict: metric statistics response, check the structure of the response [here](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.get_metric_data)

```python
def save_metric_csv(self, file_path: str, response: Union[Dict, NoneType]=None, query_preset: Union[str, NoneType]=None)
```

Query and save the metric data to a CSV file

#### Parameters:

- `file_path` (`str`): path to the file to save the metric data to
- `response` (`dict`): response retrieved with `query_ec2_metrics`.A query is performed if not provided.
- `response` (`dict`): response from `query_ec2_metrics` method
- `query_kwargs` (`dict`): kwargs to pass to the EC2 query
- `query_preset` (`str`): period preset to use for the EC2 query

```python
def save_metric_json(self, file_path: str, response: Union[Dict, NoneType]=None, query_preset: Union[str, NoneType]=None)
```

Query and save the metric data to a JSON file

#### Parameters:

- `file_path` (`str`): path to the file to save the metric data to
- `response` (`dict`): response retrieved with `query_ec2_metrics`.A query is performed if not provided.
- `response` (`dict`): response from `query_ec2_metrics` method
- `query_kwargs` (`dict`): kwargs to pass to the EC2 query
- `query_preset` (`str`): period preset to use for the EC2 query

```python
def save_metric_plot(self, file_path: str, response: Union[Dict, NoneType]=None, query_preset: Union[str, NoneType]=None)
```

Query and plot the metric data

#### Parameters:

- `file_path` (`str`): path to the file to plot the metric data to
- `kwargs` (``): keyword arguments to pass to the plotter
- `response` (`dict`): response retrieved with `query_ec2_metrics`.A query is performed if not provided.
- `response` (`dict`): response from `query_ec2_metrics` method
- `query_kwargs` (`dict`): kwargs to pass to the EC2 query
- `query_preset` (`str`): period preset to use for the EC2 query

```python
def save_response_json(self, file_path: str, response: Union[Dict, NoneType]=None, query_preset: Union[str, NoneType]=None)
```

Query and save the response data to a JSON file

#### Parameters:

- `file_path` (`str`): path to the file to save the response data to
- `response` (`dict`): response retrieved with `query_ec2_metrics`.A query is performed if not provided.
- `response` (`dict`): response from `query_ec2_metrics` method
- `query_kwargs` (`dict`): kwargs to pass to the EC2 query
- `query_preset` (`str`): period preset to use for the EC2 query

```python
def timed_metric_factory(response: dict) -> List[cloudwatcher.metric_handlers.TimedMetric]
```

Create a collection of TimedMetrics from the CloudWatch client response.

#### Parameters:

- `response` (`dict`): response from CloudWatch client

#### Returns:

- `List[TimedMetric]`: list of TimedMetric objects

## <a name="LogWatcher"></a> Class `LogWatcher`

A class for AWS CloudWatch log events retrieval and parsing

```python
def __init__(self, log_group_name: str, log_stream_name: str, start_token: Union[str, NoneType]=None, aws_access_key_id: Union[str, NoneType]=None, aws_secret_access_key: Union[str, NoneType]=None, aws_session_token: Union[str, NoneType]=None, aws_region_name: Union[str, NoneType]=None) -> None
```

Initialize LogWatcher

#### Parameters:

- `log_group_name` (`str`): The name of the log group
- `log_stream_name` (`str`): The name of the log stream
- `region_name` (`Optional[str]`): The name of the region. Defaults to 'us-east-1'
- `start_token` (`Optional[str]`): The start token to use for the query

```python
def check_log_exists(self) -> bool
```

Check if the log stream exists

#### Returns:

- `bool`: True if the log stream exists, False otherwise

```python
def format_logs_events(self, log_events: List[Dict[str, str]], regex: str='^\\[\\d+-\\d+-\\d+\\s\\d+:\\d+:\\d+(.|,)\\d+(\\]|\\s-\\s\\w+\\])', fmt_str: str='[{time} UTC] {message}') -> List[str]
```

Format log events

#### Parameters:

- `log_events` (`List[Event]`): The list of log events
- `regex` (`str`): The regex to use for extracting the timestamp
- `fmt_str` (`str`): The format string to use for formatting the log event

#### Returns:

- `List[str]`: The list of formatted log events

```python
def return_formatted_logs(self, events_limit: int=1000, max_retry_attempts: int=5) -> Tuple[str, str]
```

A generator that yields formatted log events

#### Parameters:

- `events_limit` (`Optional[int]`): The number of events to retrieve per iteration. Defaults to 1000
- `max_retry_attempts` (`Optional[int]`): The number of retry attempts. Defaults to 5

#### Returns:

- `Tuple[List[str], str]`: formatted log events and the token to use for the next query

```python
def save_log_file(self, file_path: str) -> None
```

Save the log file to the specified path

#### Parameters:

- `log_file_path` (`str`): The path to save the log file

```python
def stream_cloudwatch_logs(self, events_limit: int=1000, max_retry_attempts: int=5) -> List[Dict[str, str]]
```

A generator that retrieves desired number of log events per iteration

#### Parameters:

- `log_group_name` (`str`): The name of the log group
- `log_stream_name` (`str`): The name of the log stream
- `events_limit` (`int`): The number of events to retrieve per iteration

#### Returns:

- `List[Event]`: The list of log events

```python
def stream_formatted_logs(self, events_limit: int=1000, max_retry_attempts: int=5, sep: str='<br>') -> Tuple[List[str], str]
```

A generator that yields formatted log events

#### Parameters:

- `events_limit` (`Optional[int]`): The number of events to retrieve per iteration. Defaults to 1000
- `max_retry_attempts` (`Optional[int]`): The number of retry attempts. Defaults to 5
- `sep` (`Optional[str]`): The format string to use for formatting the log event. Defaults to "<br>"

#### Returns:

- `Tuple[List[str], str]`: The list of formatted log events and the token to use for the next query

## <a name="ResponseLogger"></a> Class `ResponseLogger`

Log the response to the console

## <a name="ResponseSaver"></a> Class `ResponseSaver`

Save the response to a file

## <a name="TimedMetricCsvSaver"></a> Class `TimedMetricCsvSaver`

Class to establish the interface for a timed metric handling

## <a name="TimedMetricJsonSaver"></a> Class `TimedMetricJsonSaver`

Class to establish the interface for a timed metric handling

## <a name="TimedMetricLogger"></a> Class `TimedMetricLogger`

Class to establish the interface for a timed metric handling

```python
def mem_to_str(size: int, precision: int=3) -> str
```

Convert bytes to human readable string

#### Parameters:

- `size` (`int`): size in bytes
- `precision` (`int`): number of decimal places

## <a name="TimedMetricPlotter"></a> Class `TimedMetricPlotter`

Class to establish the interface for a timed metric handling

## <a name="TimedMetricSummarizer"></a> Class `TimedMetricSummarizer`

Class to establish the interface for a timed metric handling

_Version Information: `cloudwatcher` v0.0.6, generated by `lucidoc` v0.4.3_
