# `cloudwatcher` Python API usage

The purpose of this page is to provide a quick overview of the `cloudwatcher` Python API. The package consists of two user-facing classes:

- `MetricWatcher`: This class is used to interact with AWS CloudWatch metrics.
- `LogWatcher`: This class is used to interact with AWS CloudWatch logs.

Both of these classes inherit from the `CloudWatcher` class.

## `MetricWatcher`: convenient interface to AWS CloudWatch metrics

`MetricWatcher` can be used to interact with AWS CloudWatch metrics. 

### `MetricWatcher` initialization

As described in the Login credentials section, the AWS credentials can be sourced from environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`.
Alternatively, you can pass the values as arguments to the `MetricWatcher` constructor.


```python
from cloudwatcher.metricwatcher import MetricWatcher
from cloudwatcher.preset import Dimension
from dotenv import load_dotenv
import os

load_dotenv()

instance_id = os.environ.get("INSTANCE_ID")
mw = MetricWatcher(
    namespace="NepheleNamespaceEC2",
    metric_name="mem_used",
    metric_id="mem_used",
    metric_unit="Bytes",
    dimensions_list=[Dimension(Name="InstanceId", Value=instance_id)],
)
```

### `MetricWatcher` presets

As you can see there are multiple arguments that can be passed to `MetricWatcher` constructor. In order to improve the UX when using `MetricWatcher` `cloudwatcher` package provides a few presets that can be used to query the data reported by `CloudWatchAgent` within certain systems. Additionally, custom presets can be defined by the user and used in the same way.

Presets are JSON-formatted files that provide parameter bundles for `MetricWatcher` initialization.

#### Usage

Listing available presets:



```python
from cloudwatcher.preset import PresetFilesInventory
from rich.console import Console

pfi = PresetFilesInventory()
Console().print(pfi.presets_table)
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                 Presets available in: /Users/stolarczykmj/code/cloudwatcher/cloudwatcher/presets                  </span>
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃<span style="color: #800080; text-decoration-color: #800080; font-weight: bold"> Name                                   </span>┃<span style="color: #800080; text-decoration-color: #800080; font-weight: bold"> Path                                                                   </span>┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ nephele_disk_used_percent              │<span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> /Users/stolarczykmj/code/cloudwatcher/cloudwatcher/presets/nephele_di… </span>│
│ nephele_mem_cached                     │<span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> /Users/stolarczykmj/code/cloudwatcher/cloudwatcher/presets/nephele_me… </span>│
│ nephele_mem                            │<span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> /Users/stolarczykmj/code/cloudwatcher/cloudwatcher/presets/nephele_me… </span>│
│ nephele_disk_used_percent_nephele_data │<span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> /Users/stolarczykmj/code/cloudwatcher/cloudwatcher/presets/nephele_di… </span>│
│ nephele_cpu_usage_user                 │<span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> /Users/stolarczykmj/code/cloudwatcher/cloudwatcher/presets/nephele_cp… </span>│
│ nephele_processes_dead                 │<span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> /Users/stolarczykmj/code/cloudwatcher/cloudwatcher/presets/nephele_pr… </span>│
│ nephele_swap_used_percent              │<span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> /Users/stolarczykmj/code/cloudwatcher/cloudwatcher/presets/nephele_sw… </span>│
│ nephele_swap_used                      │<span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> /Users/stolarczykmj/code/cloudwatcher/cloudwatcher/presets/nephele_sw… </span>│
└────────────────────────────────────────┴────────────────────────────────────────────────────────────────────────┘
</pre>



Using a preset:


```python
from cloudwatcher.preset import MetricWatcherSetup
mw_setup = MetricWatcherSetup.from_json(pfi.get_preset_path("nephele_mem"))
mw_setup.upsert_dimensions([f"InstanceId:{instance_id}"])
mw = MetricWatcher(**mw_setup.to_dict())
query_kwargs = {
    "days": 5,
    "hours": 0,
    "minutes": 0,
    "stat": "Maximum",
    "period": 60,
}
response = mw.query_ec2_metrics(**query_kwargs)
print(response)

```

    {'MetricDataResults': [{'Id': 'nephele', 'Label': 'mem_used', 'Timestamps': [], 'Values': [], 'StatusCode': 'Complete'}], 'Messages': [], 'ResponseMetadata': {'RequestId': '6f543152-1547-4c3f-a1ec-8d904e28dba2', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '6f543152-1547-4c3f-a1ec-8d904e28dba2', 'content-type': 'text/xml', 'content-length': '496', 'date': 'Mon, 31 Jul 2023 13:51:13 GMT'}, 'RetryAttempts': 0}}





### Querying AWS CloudWatch metrics

In order to specify the EC2 instace query settings (period, granularity, etc.), the user would need to provide multiple parameters. To make it easier, there are a few sensible presets that can be used to select the query settings, which are passed to `query_ec2_metrics` method. These presets are defined to query the data reported by `CloudWatchAgent` within the last day, hour or minute.

The presets can be used by passing the `query_preset` argument to the functions presented below. Alternatively, users can pass `query_kwargs` argument, which overrides the preset values.

### Logging methods

There is a method that can be used to log the metric to the screen. The EC2 instance is automatically queried if the query response is not provided.

### File saving methods

There are number of methods that can be used to save the metric data to a file. Again, the EC2 instance is automatically queried if the query response is not provided.



```python
mw.save_metric_plot(file_path=f"/tmp/{instance_id}_plot.png", query_kwargs=query_kwargs)
mw.save_metric_csv(file_path=f"/tmp/{instance_id}_metric.csv", query_kwargs=query_kwargs)
mw.save_metric_json(file_path=f"/tmp/{instance_id}_metric.json", query_kwargs=query_kwargs)
mw.save_response_json(file_path=f"/tmp/{instance_id}_response.json", query_kwargs=query_kwargs)
```

### Manual EC2 querying

For users that require more control over the EC2 instance query settings, the `query_ec2_metrics` method can be used to manually query the EC2 instance. For instance it allows to fine tune the query period settings.


```python
FINE_TUNED_SETTINGS = {
    "days": 7,
    "hours": 0,
    "minutes": 0,
    "stat": "Maximum",
    "period": 60,
}
response = mw.query_ec2_metrics(**FINE_TUNED_SETTINGS)

response["ResponseMetadata"]
```




    {'RequestId': 'a59814d4-5445-4cb8-b539-9efb7d65716f',
     'HTTPStatusCode': 200,
     'HTTPHeaders': {'x-amzn-requestid': 'a59814d4-5445-4cb8-b539-9efb7d65716f',
      'content-type': 'text/xml',
      'content-length': '4418',
      'date': 'Mon, 31 Jul 2023 13:51:13 GMT'},
     'RetryAttempts': 0}



### `TimedMetric` dataclass

Internally, the package uses `TimedMetric` dataclass to store the metric data. This dataclass is used to store the metric data and provide a convenient interface to access the data. It can be also used to interact with the metric data by the user.


```python
response = mw.query_ec2_metrics(**FINE_TUNED_SETTINGS)
timed_metric = mw.timed_metric_factory(response)[0]
print(timed_metric.__class__)
timed_metric.values[1:10]
```

    <class 'cloudwatcher.metric_handlers.TimedMetric'>





    [1051193344.0,
     22160080896.0,
     29538459648.0,
     29531140096.0,
     17124524032.0,
     29451448320.0,
     17050480640.0,
     29373624320.0,
     29358415872.0]



## `LogWatcher`: convenient interface to AWS CloudWatch logs

`LogWatcher` can be used to interact with AWS CloudWatch logs.

### `LogWatcher` initialization

As described in the Login credentials section, the AWS credentials can be sourced from environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`.
Alternatively, you can pass the values as arguments to the `LogWatcher` constructor.


```python
from cloudwatcher.logwatcher import LogWatcher
from dotenv import load_dotenv
import os

load_dotenv()
x=os.environ.get("LOG_GROUP_NAME")
y=os.environ.get("LOG_STREAM_NAME")
print(f"LOG_GROUP_NAME: {x}")
print(f"LOG_STREAM_NAME: {y}")

lw = LogWatcher(
    log_group_name=os.environ.get("LOG_GROUP_NAME"),
    log_stream_name=os.environ.get("LOG_STREAM_NAME"),
)

```

    LOG_GROUP_NAME: main-NepheleWorker
    LOG_STREAM_NAME: i-05cec4924aadbd516-job.log


Importantly, you can also provide the start token for the log, which will be used to determine the starting point of the log query.

### Log streaming

`LogWatcher` provides a convenient interface to stream the logs from AWS CloudWatch. There are 2 relevant parameters in `stream_cloudwatch_logs` method:

- `events_limit` - the maximum number of events to be returned. If the value is set to `None`, 1000 events are returned
- `max_retry_attempts` - the maximum number of retry attempts to be made if the query results with an empty log

The `stream_cloudwatch_logs` method returns a generator that yields the log events, for example in a `for` loop. In the example below , we use `next` to get the first event from the generator.


```python
streamer = lw.stream_cloudwatch_logs(events_limit=2, max_retry_attempts=2)
next(streamer)
```




    LogEventsList(events=[LogEvent(message='[2023-07-25 12:58:13,421 - INFO] Nephele, developed by BCBB/OCICB/NIAID/NIH version: 2.27.1, tag: Nephele_2023_July_19, commit: 0b87cad', timestamp=datetime.datetime(2023, 7, 25, 12, 58, 14, 403000)), LogEvent(message='[2023-07-25 12:58:13,421 - INFO] Python version: 3.7.3', timestamp=datetime.datetime(2023, 7, 25, 12, 58, 14, 403000))], next_forward_token='f/37695045377463395103684887982714400219916480157627908097/s', next_backward_token='b/37695045377463395103684887982714400219916480157627908096/s')



The log events are returned as a custom `LogEventsList` object, which conists of a list of `LogEvents` and tokens. The next token (`LogEventsList.next_forward_token`) can be used to get the next batch of log events. The token can be provided to the `LogWatcher` constructor to start streaming from the last event.

### Retrieving all logs

Alternatively, the `return_formatted_logs` method can be used to retrieve all the logs. This method returns a `Tuple[str,str]`, where the first element is the formatted log and the second element is the next token. 


```python
formatted_logs, token = lw.return_formatted_logs()

print(formatted_logs)

```

    [25-07-2023 12:58:14 UTC] Nephele, developed by BCBB/OCICB/NIAID/NIH version: 2.27.1, tag: Nephele_2023_July_19, commit: 0b87cad
    [25-07-2023 12:58:14 UTC] Python version: 3.7.3
    [25-07-2023 12:58:14 UTC] Current time: 2023-07-25 12:58
    [25-07-2023 12:58:14 UTC] Pipeline name: Biobakery
    [25-07-2023 12:58:14 UTC] Job Description:
    [25-07-2023 12:58:14 UTC] Job parameters
    [25-07-2023 12:58:14 UTC] job_id: 5bfc066feb92
    [25-07-2023 12:58:14 UTC] map_file: <_io.TextIOWrapper name='/nephele_data/inputs/N2_16S_example_mapping_one_corrected.txt' mode='r' encoding='latin-1'>
    [25-07-2023 12:58:14 UTC] data_type: WGS_PE
    [25-07-2023 12:58:14 UTC] threads: 12
    [25-07-2023 12:58:14 UTC] local_jobs: 4
    [25-07-2023 12:58:14 UTC] strainphlan: False
    [25-07-2023 12:58:14 UTC] keep: False
    [25-07-2023 12:58:14 UTC] project_name: 5bfc066feb92
    [25-07-2023 12:58:14 UTC] inputs_dir: None
    [25-07-2023 12:58:14 UTC] outputs_dir: None
    [25-07-2023 12:58:14 UTC] Results manager initialized. Results registry path: /mnt/EFS/user_uploads/5bfc066feb92/outputs/5bfc066feb92_results_registry.json
    [25-07-2023 12:58:14 UTC] Skipping FASTQ file validation
    [25-07-2023 12:58:14 UTC] Renaming paired end files.
    [25-07-2023 12:58:14 UTC] Inputs directory: /nephele_data/outputs/renamed_inputs/
    [25-07-2023 12:58:14 UTC] Running Whole Metagenome Shotgun Workflow (wmgx).
    [25-07-2023 12:58:19 UTC] run --mount type=bind,source=/mnt/EFS/dbs/biobakery_workflows_databases_3.0.0.a.7,target=/opt/biobakery_workflows_databases --mount type=bind,source=/nephele_data/,target=/nephele_data/ --user www-data biobakery/nephele2:3.0.0.a.7 biobakery_workflows wmgx --input-extension fastq --threads 12 --input /nephele_data/outputs/renamed_inputs/ --output /nephele_data/outputs/ --skip-nothing --local-jobs 4 --taxonomic-profiling-options "-x mpa_v30_CHOCOPhlAn_201901" --bypass-strain-profiling
    [25-07-2023 13:38:00 UTC] Create wmgx_vis output directory: /nephele_data/outputs/wmgx_vis
    [25-07-2023 13:38:00 UTC] Checking output files from wmgx workflow that are required by wmgx_vis workflow.
    [25-07-2023 13:38:00 UTC] Running Visualization for Whole Metagenome Shotgun Workflow (wmgx_vis).
    [25-07-2023 13:38:04 UTC] run --mount type=bind,source=/mnt/EFS/dbs/biobakery_workflows_databases_3.0.0.a.7,target=/opt/biobakery_workflows_databases --mount type=bind,source=/nephele_data/,target=/nephele_data/ --user www-data biobakery/nephele2:3.0.0.a.7 biobakery_workflows wmgx_vis --input /nephele_data/outputs/ --project-name '5bfc066feb92' --format html --output /nephele_data/outputs/wmgx_vis --introduction-text "The data was run through the standard workflow for whole metagenome shotgun sequencing  with the exception of strain profiling (StrainPhlAn).  Details of the pipelines can be found in the <a href=https://github.com/biobakery/biobakery/wiki/biobakery_workflows#2-metagenome-profiling>bioBakery Workflows Tutorial</a>."
    [25-07-2023 13:38:04 UTC] Checking output files from wmgx_vis pipeline.
    [25-07-2023 13:38:04 UTC] Pipeline Error:
    [25-07-2023 13:38:04 UTC] ('/nephele_data/outputs/wmgx_vis/wmgx_report.html does not exist.\n', 'Job ID Unknown')
    [25-07-2023 13:38:04 UTC] A step in the biobakery workflows may have failed. Check anadama.log files.
    [25-07-2023 13:38:04 UTC] 
    [25-07-2023 13:38:04 UTC] Cleaning up intermediate files.
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22350.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22831.trimmed.single.2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22192.trimmed.single.2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22350.trimmed.single.1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22192_hg37dec_v0.1_bowtie2_paired_contam_2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22350_hg37dec_v0.1_bowtie2_unmatched_1_contam.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22192.repeats.removed.unmatched.2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22831.repeats.removed.1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22831_unmatched_1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22350_hg37dec_v0.1_bowtie2_unmatched_2_contam.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22831.trimmed.1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22350.trimmed.1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22192.trimmed.1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22831_hg37dec_v0.1_bowtie2_paired_contam_1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22350.repeats.removed.unmatched.1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22831_hg37dec_v0.1_bowtie2_paired_contam_2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22831.trimmed.2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22192.repeats.removed.2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22831.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22192.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22350_paired_2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22831.repeats.removed.unmatched.1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22350.repeats.removed.2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22831_paired_2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22350_hg37dec_v0.1_bowtie2_paired_contam_1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22192_paired_2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22192_hg37dec_v0.1_bowtie2_paired_contam_1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22350_unmatched_2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22350_hg37dec_v0.1_bowtie2_paired_contam_2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22192_hg37dec_v0.1_bowtie2_unmatched_2_contam.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22192_hg37dec_v0.1_bowtie2_unmatched_1_contam.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22350.repeats.removed.unmatched.2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22350.trimmed.single.2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22192.trimmed.2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22831_unmatched_2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22831.repeats.removed.2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22831.repeats.removed.unmatched.2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22831_hg37dec_v0.1_bowtie2_unmatched_1_contam.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22350_paired_1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22831.trimmed.single.1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22192.trimmed.single.1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22192_unmatched_1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22350_unmatched_1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22192_paired_1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22192.repeats.removed.unmatched.1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22350.repeats.removed.1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22831_paired_1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22831_hg37dec_v0.1_bowtie2_unmatched_2_contam.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22192.repeats.removed.1.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22192_unmatched_2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/kneaddata/main/A22350.trimmed.2.fastq
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/metaphlan/main/A22192_bowtie2.sam
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/metaphlan/main/A22350_bowtie2.sam
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/metaphlan/main/A22831_bowtie2.sam
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/humann/main/A22192_humann_temp
    [25-07-2023 13:38:04 UTC] Removing /nephele_data/outputs/humann/main/A22831_humann_temp
    [25-07-2023 13:38:09 UTC] Removing /nephele_data/outputs/humann/main/A22350_humann_temp

