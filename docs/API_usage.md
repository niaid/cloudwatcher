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

    {'MetricDataResults': [{'Id': 'nephele', 'Label': 'mem_used', 'Timestamps': [datetime.datetime(2023, 7, 19, 16, 45, tzinfo=tzutc()), datetime.datetime(2023, 7, 19, 16, 44, tzinfo=tzutc()), datetime.datetime(2023, 7, 19, 16, 43, tzinfo=tzutc()), datetime.datetime(2023, 7, 19, 16, 42, tzinfo=tzutc()), datetime.datetime(2023, 7, 19, 16, 41, tzinfo=tzutc()), datetime.datetime(2023, 7, 19, 16, 40, tzinfo=tzutc()), datetime.datetime(2023, 7, 19, 16, 39, tzinfo=tzutc()), datetime.datetime(2023, 7, 19, 16, 38, tzinfo=tzutc()), datetime.datetime(2023, 7, 19, 16, 37, tzinfo=tzutc()), datetime.datetime(2023, 7, 19, 16, 36, tzinfo=tzutc()), datetime.datetime(2023, 7, 19, 16, 35, tzinfo=tzutc()), datetime.datetime(2023, 7, 19, 16, 34, tzinfo=tzutc())], 'Values': [486064128.0, 485814272.0, 4685066240.0, 6207594496.0, 4992217088.0, 4720185344.0, 2435854336.0, 2444738560.0, 2400739328.0, 11007488000.0, 2191474688.0, 576376832.0], 'StatusCode': 'Complete'}], 'Messages': [], 'ResponseMetadata': {'RequestId': 'bbc8d20e-7879-447e-87e5-019b3769220f', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': 'bbc8d20e-7879-447e-87e5-019b3769220f', 'content-type': 'text/xml', 'content-length': '1596', 'date': 'Wed, 19 Jul 2023 18:35:02 GMT'}, 'RetryAttempts': 0}}





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


    
![png](API_usage_files/API_usage_10_0.png)
    


### Manual EC2 querying

For users that require more control over the EC2 instance query settings, the `query_ec2_metrics` method can be used to manually query the EC2 instance. For instance it allows to fine tune the query period settings.


```python
FINE_TUNED_SETTINGS = {
    "days": 5,
    "hours": 0,
    "minutes": 0,
    "stat": "Maximum",
    "period": 60,
}
response = mw.query_ec2_metrics(**FINE_TUNED_SETTINGS)

response["ResponseMetadata"]
```




    {'RequestId': '256d262e-488a-42bc-9197-2fcd4df82e98',
     'HTTPStatusCode': 200,
     'HTTPHeaders': {'x-amzn-requestid': '256d262e-488a-42bc-9197-2fcd4df82e98',
      'content-type': 'text/xml',
      'content-length': '1596',
      'date': 'Wed, 19 Jul 2023 18:35:04 GMT'},
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





    [485814272.0,
     4685066240.0,
     6207594496.0,
     4992217088.0,
     4720185344.0,
     2435854336.0,
     2444738560.0,
     2400739328.0,
     11007488000.0]



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

lw = LogWatcher(
    log_group_name=os.environ.get("LOG_GROUP_NAME"),
    log_stream_name=os.environ.get("LOG_STREAM_NAME"),
)
```

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




    LogEventsList(events=[LogEvent(message='[2023-07-19 12:34:48,735 - INFO] Nephele, developed by BCBB/OCICB/NIAID/NIH version: 2.27.1, tag: Nephele_2023_July_19, commit: dce18e5', timestamp=datetime.datetime(2023, 7, 19, 12, 34, 48, 833000)), LogEvent(message='[2023-07-19 12:34:48,736 - INFO] Python version: 3.9.2', timestamp=datetime.datetime(2023, 7, 19, 12, 34, 48, 833000))], next_forward_token='f/37683453325894048129959718411585392236426944928309968897/s', next_backward_token='b/37683453325894048129959718411585392236426944928309968896/s')



The log events are returned as a custom `LogEventsList` object, which conists of a list of `LogEvents` and tokens. The next token (`LogEventsList.next_forward_token`) can be used to get the next batch of log events. The token can be provided to the `LogWatcher` constructor to start streaming from the last event.

### Retrieving all logs

Alternatively, the `return_formatted_logs` method can be used to retrieve all the logs. This method returns a `Tuple[str,str]`, where the first element is the formatted log and the second element is the next token. 


```python
formatted_logs, token = lw.return_formatted_logs()

print(formatted_logs)

```

    [19-07-2023 12:34:48 UTC] Nephele, developed by BCBB/OCICB/NIAID/NIH version: 2.27.1, tag: Nephele_2023_July_19, commit: dce18e5
    [19-07-2023 12:34:48 UTC] Python version: 3.9.2
    [19-07-2023 12:34:48 UTC] Current time: 2023-07-19 12:34
    [19-07-2023 12:34:49 UTC] Pipeline name: DADA2
    [19-07-2023 12:34:49 UTC] Job Description:
    [19-07-2023 12:34:49 UTC] Job parameters
    [19-07-2023 12:34:49 UTC] job_id: b73de8bfdd22
    [19-07-2023 12:34:49 UTC] inputs_dir: None
    [19-07-2023 12:34:49 UTC] outputs_dir: None
    [19-07-2023 12:34:49 UTC] map_file: <_io.TextIOWrapper name='/nephele_data/inputs/N2_16S_example_mapping_file_3_corrected.txt' mode='r' encoding='UTF-8'>
    [19-07-2023 12:34:49 UTC] data_type: PE
    [19-07-2023 12:34:49 UTC] wurlitzer_stdout: file
    [19-07-2023 12:34:49 UTC] wurlitzer_stderr: file
    [19-07-2023 12:34:49 UTC] ion_torrent: False
    [19-07-2023 12:34:49 UTC] trimleft_fwd: 0
    [19-07-2023 12:34:49 UTC] trimleft_rev: 0
    [19-07-2023 12:34:49 UTC] maxee: 5
    [19-07-2023 12:34:49 UTC] trunclen_fwd: 0
    [19-07-2023 12:34:49 UTC] trunclen_rev: 0
    [19-07-2023 12:34:49 UTC] truncq: 4
    [19-07-2023 12:34:49 UTC] just_concatenate: False
    [19-07-2023 12:34:49 UTC] maxmismatch: 0
    [19-07-2023 12:34:49 UTC] trim_overhang: False
    [19-07-2023 12:34:49 UTC] chimera: True
    [19-07-2023 12:34:49 UTC] ref_db: sv138.1
    [19-07-2023 12:34:49 UTC] taxmethod: rdp
    [19-07-2023 12:34:49 UTC] sampling_depth: None
    [19-07-2023 12:34:49 UTC] pseudopool: False
    [19-07-2023 12:34:49 UTC] minboot: 80
    [19-07-2023 12:34:49 UTC] allowmultiplespecies: False
    [19-07-2023 12:34:49 UTC] Results manager initialized. Results registry path: /mnt/EFS/user_uploads/b73de8bfdd22/outputs/b73de8bfdd22_results_registry.json
    [19-07-2023 12:34:49 UTC] Checking Mapfile for Gzipped inputs.
    [19-07-2023 12:34:49 UTC] Gzipped files listed in map file, attempting to rm .gz extension.
    [19-07-2023 12:34:51 UTC] Done. Attempting file decompression.
    [19-07-2023 12:34:51 UTC] Finished decompression.
    [19-07-2023 12:34:55 UTC] Skipping FASTQ file validation
    [19-07-2023 12:35:04 UTC] Reference DB (sv138.1) checksum: 6b41db7139834c71171f8ce5b5918fc6
    [19-07-2023 12:35:05 UTC] Taxonomy assignemnt DB checksum: f21c2d97c79ff07c17949a9622371a4c
    [19-07-2023 12:35:05 UTC] Running dada2nephele.R with command:
    [19-07-2023 12:35:09 UTC] Rscript /usr/local/src/nephele2/pipelines/DADA2/dada2nephele/R/dada2nephele.R  --datadir /nephele_data/inputs/ --outdir /nephele_data/outputs/ --mapfile /nephele_data/outputs/N2_16S_example_mapping_file_3_corrected.txt.no_gz --logfilename /var/log/job.log --nthread 12 --maxEE 5 --truncQ 4 --maxMismatch 0 --chimera --data_type PE --minBoot 80 --no_MultipleSpecies --trimLeft_R1 0 --trimLeft_R2 0 --truncLen_R1 0 --truncLen_R2 0 --taxmethod rdp --refdb /mnt/EFS/dbs/dada2_silva_v138.1/silva_nr99_v138.1_train_set.fa.gz --refdb_species /mnt/EFS/dbs/dada2_silva_v138.1/silva_species_assignment_v138.1.fa.gz
    [19-07-2023 12:35:16 UTC] R version 4.3.1 (2023-06-16)
    [19-07-2023 12:35:16 UTC] Platform: x86_64-pc-linux-gnu (64-bit)
    [19-07-2023 12:35:16 UTC] Running under: Debian GNU/Linux 11 (bullseye)
    [19-07-2023 12:35:16 UTC] Matrix products: default
    [19-07-2023 12:35:16 UTC] BLAS:   /usr/lib/x86_64-linux-gnu/blas/libblas.so.3.9.0
    [19-07-2023 12:35:16 UTC] LAPACK: /usr/lib/x86_64-linux-gnu/lapack/liblapack.so.3.9.0
    [19-07-2023 12:35:16 UTC] locale:
     [1] LC_CTYPE=C.UTF-8       LC_NUMERIC=C           LC_TIME=C.UTF-8       
     [4] LC_COLLATE=C.UTF-8     LC_MONETARY=C.UTF-8    LC_MESSAGES=C.UTF-8   
     [7] LC_PAPER=C.UTF-8       LC_NAME=C              LC_ADDRESS=C
    [19-07-2023 12:35:16 UTC] [10] LC_TELEPHONE=C         LC_MEASUREMENT=C.UTF-8 LC_IDENTIFICATION=C
    [19-07-2023 12:35:16 UTC] time zone: America/New_York
    [19-07-2023 12:35:16 UTC] tzcode source: system (glibc)
    [19-07-2023 12:35:16 UTC] attached base packages:
    [19-07-2023 12:35:16 UTC] [1] stats     graphics  grDevices utils     datasets  methods   base
    [19-07-2023 12:35:16 UTC] other attached packages:
    [19-07-2023 12:35:16 UTC] [1] dada2_1.28.0 Rcpp_1.0.11  docopt_0.7.1
    [19-07-2023 12:35:16 UTC] loaded via a namespace (and not attached):
     [1] utf8_1.2.3                  generics_0.1.3             
     [3] bitops_1.0-7                stringi_1.7.12             
     [5] jpeg_0.1-10                 lattice_0.20-45            
     [7] magrittr_2.0.3              grid_4.3.1                 
     [9] RColorBrewer_1.1-3          iterators_1.0.14
    [19-07-2023 12:35:16 UTC] [11] foreach_1.5.2               plyr_1.8.8
    [19-07-2023 12:35:16 UTC] [13] Matrix_1.5-3                GenomeInfoDb_1.36.1
    [19-07-2023 12:35:16 UTC] [15] fansi_1.0.4                 scales_1.2.1
    [19-07-2023 12:35:16 UTC] [17] Biostrings_2.68.1           codetools_0.2-19
    [19-07-2023 12:35:16 UTC] [19] cli_3.6.1                   ShortRead_1.58.0
    [19-07-2023 12:35:16 UTC] [21] rlang_1.1.1                 crayon_1.5.2
    [19-07-2023 12:35:16 UTC] [23] XVector_0.40.0              Biobase_2.60.0
    [19-07-2023 12:35:16 UTC] [25] munsell_0.5.0               DelayedArray_0.26.6
    [19-07-2023 12:35:16 UTC] [27] S4Arrays_1.0.4              tools_4.3.1
    [19-07-2023 12:35:16 UTC] [29] parallel_4.3.1              reshape2_1.4.4
    [19-07-2023 12:35:16 UTC] [31] deldir_1.0-9                BiocParallel_1.34.2
    [19-07-2023 12:35:16 UTC] [33] dplyr_1.1.2                 interp_1.1-4
    [19-07-2023 12:35:16 UTC] [35] colorspace_2.1-0            ggplot2_3.4.2
    [19-07-2023 12:35:16 UTC] [37] GenomeInfoDbData_1.2.10     Rsamtools_2.16.0
    [19-07-2023 12:35:16 UTC] [39] hwriter_1.3.2.1             SummarizedExperiment_1.30.2
    [19-07-2023 12:35:16 UTC] [41] BiocGenerics_0.46.0         png_0.1-8
    [19-07-2023 12:35:16 UTC] [43] vctrs_0.6.3                 R6_2.5.1
    [19-07-2023 12:35:16 UTC] [45] matrixStats_1.0.0           stats4_4.3.1
    [19-07-2023 12:35:16 UTC] [47] lifecycle_1.0.3             stringr_1.5.0
    [19-07-2023 12:35:16 UTC] [49] zlibbioc_1.46.0             S4Vectors_0.38.1
    [19-07-2023 12:35:16 UTC] [51] IRanges_2.34.1              pkgconfig_2.0.3
    [19-07-2023 12:35:16 UTC] [53] RcppParallel_5.1.7          pillar_1.9.0
    [19-07-2023 12:35:16 UTC] [55] gtable_0.3.3                glue_1.6.2
    [19-07-2023 12:35:16 UTC] [57] tibble_3.2.1                GenomicAlignments_1.36.0
    [19-07-2023 12:35:16 UTC] [59] GenomicRanges_1.52.0        tidyselect_1.2.0
    [19-07-2023 12:35:16 UTC] [61] MatrixGenerics_1.12.2       latticeExtra_0.6-30
    [19-07-2023 12:35:16 UTC] [63] compiler_4.3.1              import_1.3.0
    [19-07-2023 12:35:16 UTC] [65] RCurl_1.98-1.12
    [19-07-2023 12:35:16 UTC] Taxonomic Reference Database
    [19-07-2023 12:35:16 UTC] /mnt/EFS/dbs/dada2_silva_v138.1/silva_nr99_v138.1_train_set.fa.gz
    [19-07-2023 12:35:16 UTC] /mnt/EFS/dbs/dada2_silva_v138.1/silva_species_assignment_v138.1.fa.gz
    [19-07-2023 12:35:16 UTC] Reading in map file  /nephele_data/outputs/N2_16S_example_mapping_file_3_corrected.txt.no_gz
    [19-07-2023 12:35:16 UTC] Printing dada algorithm options.
     [1]           16        FALSE           -8         TRUE         TRUE
     [6]                      0.42            5            0           10
    [19-07-2023 12:35:16 UTC] [11]            1            1            1           -4 0.000000....
    [19-07-2023 12:35:16 UTC] [16] 0.000000....       0.0001          Inf            2            2
    [19-07-2023 12:35:16 UTC] [21]         TRUE         TRUE         TRUE
    [19-07-2023 12:35:16 UTC] Paired End
    [19-07-2023 12:35:20 UTC] pqp <- lapply(readslist, FUN = function(x) { ppp <- plotQualityProfile(file.path(datadir, x)); ppp$facet$params$ncol <- 4; ppp })
    [19-07-2023 12:35:53 UTC] Saving quality profile plots to quality_Profile_R*.pdf
    [19-07-2023 12:35:57 UTC] out <- filterAndTrim(fwd=file.path(datadir,readslist$R1), filt=file.path(filt.dir,trimlist$R1),rev=file.path(datadir,readslist$R2), filt.rev=file.path(filt.dir,trimlist$R2),  maxEE=5, trimLeft=c(0, 0), truncQ=4, truncLen = c(0, 0), rm.phix=TRUE, compress=TRUE, verbose=TRUE, multithread=12, minLen=50)
    [19-07-2023 12:36:01 UTC] Creating output directory: /nephele_data/outputs/filtered_data
    [19-07-2023 12:36:03 UTC] reads.in reads.out
    [19-07-2023 12:36:03 UTC] 22831_S41_R1_subsample.fastq     25000     20511
    [19-07-2023 12:36:03 UTC] 22833_S45_R1_subsample.fastq     25000     20346
    [19-07-2023 12:36:03 UTC] 22349_S26_R1_subsample.fastq     25000     20929
    [19-07-2023 12:36:03 UTC] 22192_S22_R1_subsample.fastq     25000     21446
    [19-07-2023 12:36:03 UTC] 22187_S19_R1_subsample.fastq     25000     20753
    [19-07-2023 12:36:03 UTC] 22061_S5_R1_subsample.fastq      25000     20200
    [19-07-2023 12:36:03 UTC] 22057_S2_R1_subsample.fastq      25000     20969
    [19-07-2023 12:36:03 UTC] 22145_S14_R1_subsample.fastq     25000     18613
    [19-07-2023 12:36:03 UTC] 22350_S27_R1_subsample.fastq     25000     19778
    [19-07-2023 12:36:03 UTC] 23572_S307_R1_subsample.fastq    25000     17656
    [19-07-2023 12:36:03 UTC] Saved Vega-Lite data to: /nephele_data/outputs/readsInReadsOutVegaJSON.json
    [19-07-2023 12:36:03 UTC] Checking that trimmed files exist.
    [19-07-2023 12:36:04 UTC] list2env(checktrimfiles(A, filt.dir, trimlist), envir = environment())
    [19-07-2023 12:36:08 UTC] err <- lapply(trimlist, function(x) learnErrors(x, multithread=12, nbases=100000000,randomize=FALSE))
    [19-07-2023 12:36:14 UTC] 52511424 total bases in 201201 reads from 10 samples will be used for learning the error rates.
    [19-07-2023 12:37:36 UTC] 52366403 total bases in 201201 reads from 10 samples will be used for learning the error rates.
    [19-07-2023 12:39:31 UTC] pe <- lapply(err, function(x) plotErrors(x, nominalQ=TRUE))
    [19-07-2023 12:39:31 UTC] Saving 7 x 7 in image
    [19-07-2023 12:39:32 UTC] Warning: Transformation introduced infinite values in continuous y-axis
    [19-07-2023 12:39:32 UTC] Saving 7 x 7 in image
    [19-07-2023 12:39:33 UTC] Warning: Transformation introduced infinite values in continuous y-axis
    [19-07-2023 12:39:33 UTC] Saving 7 x 7 in image
    [19-07-2023 12:39:34 UTC] Warning: Transformation introduced infinite values in continuous y-axis
    [19-07-2023 12:39:34 UTC] Saving 7 x 7 in image
    [19-07-2023 12:39:35 UTC] Warning: Transformation introduced infinite values in continuous y-axis
    [19-07-2023 12:39:35 UTC] derep <- lapply(trimlist, function(x) derepFastq(x[sample], verbose=TRUE))
    [19-07-2023 12:39:35 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22831_S41_R1_subsample_trim.fastq.gz
    [19-07-2023 12:39:35 UTC] Encountered 10011 unique sequences from 20511 total sequences read.
    [19-07-2023 12:39:36 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22831_S41_R2_subsample_trim.fastq.gz
    [19-07-2023 12:39:36 UTC] Encountered 16353 unique sequences from 20511 total sequences read.
    [19-07-2023 12:39:38 UTC] dd <- sapply(nameslist, function(x) dada(derep[[x]], err=err[[x]], multithread=12, verbose=F, priors = pseudo_priors[[x]]), USE.NAMES=TRUE, simplify=FALSE)
    [19-07-2023 12:39:38 UTC] R1: 132 sequence variants were inferred from 10011 input unique sequences. R2: 106 sequence variants were inferred from 16353 input unique sequences.
    [19-07-2023 12:39:39 UTC] mergePairs(dd$R1, derep$R1, dd$R2, derep$R2, verbose=TRUE, minOverlap=12, trimOverhang=FALSE, maxMismatch=0, justConcatenate=FALSE)
    [19-07-2023 12:39:39 UTC] 14245 paired-reads (in 245 unique pairings) successfully merged out of 19342 (in 799 pairings) input.
    [19-07-2023 12:39:39 UTC] derep <- lapply(trimlist, function(x) derepFastq(x[sample], verbose=TRUE))
    [19-07-2023 12:39:40 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22833_S45_R1_subsample_trim.fastq.gz
    [19-07-2023 12:39:40 UTC] Encountered 12613 unique sequences from 20346 total sequences read.
    [19-07-2023 12:39:40 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22833_S45_R2_subsample_trim.fastq.gz
    [19-07-2023 12:39:40 UTC] Encountered 18675 unique sequences from 20346 total sequences read.
    [19-07-2023 12:39:44 UTC] dd <- sapply(nameslist, function(x) dada(derep[[x]], err=err[[x]], multithread=12, verbose=F, priors = pseudo_priors[[x]]), USE.NAMES=TRUE, simplify=FALSE)
    [19-07-2023 12:39:44 UTC] R1: 268 sequence variants were inferred from 12613 input unique sequences. R2: 82 sequence variants were inferred from 18675 input unique sequences.
    [19-07-2023 12:39:44 UTC] mergePairs(dd$R1, derep$R1, dd$R2, derep$R2, verbose=TRUE, minOverlap=12, trimOverhang=FALSE, maxMismatch=0, justConcatenate=FALSE)
    [19-07-2023 12:39:44 UTC] 10806 paired-reads (in 98 unique pairings) successfully merged out of 16476 (in 400 pairings) input.
    [19-07-2023 12:39:44 UTC] derep <- lapply(trimlist, function(x) derepFastq(x[sample], verbose=TRUE))
    [19-07-2023 12:39:44 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22349_S26_R1_subsample_trim.fastq.gz
    [19-07-2023 12:39:44 UTC] Encountered 11655 unique sequences from 20929 total sequences read.
    [19-07-2023 12:39:45 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22349_S26_R2_subsample_trim.fastq.gz
    [19-07-2023 12:39:45 UTC] Encountered 17146 unique sequences from 20929 total sequences read.
    [19-07-2023 12:39:48 UTC] dd <- sapply(nameslist, function(x) dada(derep[[x]], err=err[[x]], multithread=12, verbose=F, priors = pseudo_priors[[x]]), USE.NAMES=TRUE, simplify=FALSE)
    [19-07-2023 12:39:48 UTC] R1: 175 sequence variants were inferred from 11655 input unique sequences. R2: 95 sequence variants were inferred from 17146 input unique sequences.
    [19-07-2023 12:39:48 UTC] mergePairs(dd$R1, derep$R1, dd$R2, derep$R2, verbose=TRUE, minOverlap=12, trimOverhang=FALSE, maxMismatch=0, justConcatenate=FALSE)
    [19-07-2023 12:39:49 UTC] 12735 paired-reads (in 161 unique pairings) successfully merged out of 18253 (in 738 pairings) input.
    [19-07-2023 12:39:49 UTC] derep <- lapply(trimlist, function(x) derepFastq(x[sample], verbose=TRUE))
    [19-07-2023 12:39:49 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22192_S22_R1_subsample_trim.fastq.gz
    [19-07-2023 12:39:49 UTC] Encountered 10687 unique sequences from 21446 total sequences read.
    [19-07-2023 12:39:49 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22192_S22_R2_subsample_trim.fastq.gz
    [19-07-2023 12:39:49 UTC] Encountered 16476 unique sequences from 21446 total sequences read.
    [19-07-2023 12:39:52 UTC] dd <- sapply(nameslist, function(x) dada(derep[[x]], err=err[[x]], multithread=12, verbose=F, priors = pseudo_priors[[x]]), USE.NAMES=TRUE, simplify=FALSE)
    [19-07-2023 12:39:52 UTC] R1: 130 sequence variants were inferred from 10687 input unique sequences. R2: 95 sequence variants were inferred from 16476 input unique sequences.
    [19-07-2023 12:39:53 UTC] mergePairs(dd$R1, derep$R1, dd$R2, derep$R2, verbose=TRUE, minOverlap=12, trimOverhang=FALSE, maxMismatch=0, justConcatenate=FALSE)
    [19-07-2023 12:39:53 UTC] 17599 paired-reads (in 177 unique pairings) successfully merged out of 19561 (in 513 pairings) input.
    [19-07-2023 12:39:53 UTC] derep <- lapply(trimlist, function(x) derepFastq(x[sample], verbose=TRUE))
    [19-07-2023 12:39:53 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22187_S19_R1_subsample_trim.fastq.gz
    [19-07-2023 12:39:53 UTC] Encountered 10100 unique sequences from 20753 total sequences read.
    [19-07-2023 12:39:53 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22187_S19_R2_subsample_trim.fastq.gz
    [19-07-2023 12:39:53 UTC] Encountered 16901 unique sequences from 20753 total sequences read.
    [19-07-2023 12:39:56 UTC] dd <- sapply(nameslist, function(x) dada(derep[[x]], err=err[[x]], multithread=12, verbose=F, priors = pseudo_priors[[x]]), USE.NAMES=TRUE, simplify=FALSE)
    [19-07-2023 12:39:56 UTC] R1: 140 sequence variants were inferred from 10100 input unique sequences. R2: 99 sequence variants were inferred from 16901 input unique sequences.
    [19-07-2023 12:39:56 UTC] mergePairs(dd$R1, derep$R1, dd$R2, derep$R2, verbose=TRUE, minOverlap=12, trimOverhang=FALSE, maxMismatch=0, justConcatenate=FALSE)
    [19-07-2023 12:39:56 UTC] 17011 paired-reads (in 183 unique pairings) successfully merged out of 18987 (in 418 pairings) input.
    [19-07-2023 12:39:56 UTC] derep <- lapply(trimlist, function(x) derepFastq(x[sample], verbose=TRUE))
    [19-07-2023 12:39:56 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22061_S5_R1_subsample_trim.fastq.gz
    [19-07-2023 12:39:56 UTC] Encountered 11283 unique sequences from 20200 total sequences read.
    [19-07-2023 12:39:57 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22061_S5_R2_subsample_trim.fastq.gz
    [19-07-2023 12:39:57 UTC] Encountered 17350 unique sequences from 20200 total sequences read.
    [19-07-2023 12:39:59 UTC] dd <- sapply(nameslist, function(x) dada(derep[[x]], err=err[[x]], multithread=12, verbose=F, priors = pseudo_priors[[x]]), USE.NAMES=TRUE, simplify=FALSE)
    [19-07-2023 12:39:59 UTC] R1: 186 sequence variants were inferred from 11283 input unique sequences. R2: 83 sequence variants were inferred from 17350 input unique sequences.
    [19-07-2023 12:39:59 UTC] mergePairs(dd$R1, derep$R1, dd$R2, derep$R2, verbose=TRUE, minOverlap=12, trimOverhang=FALSE, maxMismatch=0, justConcatenate=FALSE)
    [19-07-2023 12:39:59 UTC] 14630 paired-reads (in 133 unique pairings) successfully merged out of 17632 (in 343 pairings) input.
    [19-07-2023 12:39:59 UTC] derep <- lapply(trimlist, function(x) derepFastq(x[sample], verbose=TRUE))
    [19-07-2023 12:40:00 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22057_S2_R1_subsample_trim.fastq.gz
    [19-07-2023 12:40:00 UTC] Encountered 9268 unique sequences from 20969 total sequences read.
    [19-07-2023 12:40:00 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22057_S2_R2_subsample_trim.fastq.gz
    [19-07-2023 12:40:00 UTC] Encountered 15736 unique sequences from 20969 total sequences read.
    [19-07-2023 12:40:02 UTC] dd <- sapply(nameslist, function(x) dada(derep[[x]], err=err[[x]], multithread=12, verbose=F, priors = pseudo_priors[[x]]), USE.NAMES=TRUE, simplify=FALSE)
    [19-07-2023 12:40:02 UTC] R1: 151 sequence variants were inferred from 9268 input unique sequences. R2: 148 sequence variants were inferred from 15736 input unique sequences.
    [19-07-2023 12:40:03 UTC] mergePairs(dd$R1, derep$R1, dd$R2, derep$R2, verbose=TRUE, minOverlap=12, trimOverhang=FALSE, maxMismatch=0, justConcatenate=FALSE)
    [19-07-2023 12:40:03 UTC] 16865 paired-reads (in 269 unique pairings) successfully merged out of 20052 (in 475 pairings) input.
    [19-07-2023 12:40:03 UTC] derep <- lapply(trimlist, function(x) derepFastq(x[sample], verbose=TRUE))
    [19-07-2023 12:40:03 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22145_S14_R1_subsample_trim.fastq.gz
    [19-07-2023 12:40:03 UTC] Encountered 9540 unique sequences from 18613 total sequences read.
    [19-07-2023 12:40:03 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22145_S14_R2_subsample_trim.fastq.gz
    [19-07-2023 12:40:03 UTC] Encountered 16815 unique sequences from 18613 total sequences read.
    [19-07-2023 12:40:05 UTC] dd <- sapply(nameslist, function(x) dada(derep[[x]], err=err[[x]], multithread=12, verbose=F, priors = pseudo_priors[[x]]), USE.NAMES=TRUE, simplify=FALSE)
    [19-07-2023 12:40:05 UTC] R1: 222 sequence variants were inferred from 9540 input unique sequences. R2: 79 sequence variants were inferred from 16815 input unique sequences.
    [19-07-2023 12:40:06 UTC] mergePairs(dd$R1, derep$R1, dd$R2, derep$R2, verbose=TRUE, minOverlap=12, trimOverhang=FALSE, maxMismatch=0, justConcatenate=FALSE)
    [19-07-2023 12:40:06 UTC] 12534 paired-reads (in 144 unique pairings) successfully merged out of 15578 (in 352 pairings) input.
    [19-07-2023 12:40:06 UTC] derep <- lapply(trimlist, function(x) derepFastq(x[sample], verbose=TRUE))
    [19-07-2023 12:40:07 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22350_S27_R1_subsample_trim.fastq.gz
    [19-07-2023 12:40:07 UTC] Encountered 12092 unique sequences from 19778 total sequences read.
    [19-07-2023 12:40:07 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/22350_S27_R2_subsample_trim.fastq.gz
    [19-07-2023 12:40:07 UTC] Encountered 17357 unique sequences from 19778 total sequences read.
    [19-07-2023 12:40:10 UTC] dd <- sapply(nameslist, function(x) dada(derep[[x]], err=err[[x]], multithread=12, verbose=F, priors = pseudo_priors[[x]]), USE.NAMES=TRUE, simplify=FALSE)
    [19-07-2023 12:40:10 UTC] R1: 214 sequence variants were inferred from 12092 input unique sequences. R2: 94 sequence variants were inferred from 17357 input unique sequences.
    [19-07-2023 12:40:10 UTC] mergePairs(dd$R1, derep$R1, dd$R2, derep$R2, verbose=TRUE, minOverlap=12, trimOverhang=FALSE, maxMismatch=0, justConcatenate=FALSE)
    [19-07-2023 12:40:10 UTC] 12376 paired-reads (in 128 unique pairings) successfully merged out of 16356 (in 470 pairings) input.
    [19-07-2023 12:40:10 UTC] derep <- lapply(trimlist, function(x) derepFastq(x[sample], verbose=TRUE))
    [19-07-2023 12:40:10 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/23572_S307_R1_subsample_trim.fastq.gz
    [19-07-2023 12:40:10 UTC] Encountered 9005 unique sequences from 17656 total sequences read.
    [19-07-2023 12:40:11 UTC] Dereplicating sequence entries in Fastq file: /nephele_data/outputs/filtered_data/23572_S307_R2_subsample_trim.fastq.gz
    [19-07-2023 12:40:11 UTC] Encountered 16088 unique sequences from 17656 total sequences read.
    [19-07-2023 12:40:12 UTC] dd <- sapply(nameslist, function(x) dada(derep[[x]], err=err[[x]], multithread=12, verbose=F, priors = pseudo_priors[[x]]), USE.NAMES=TRUE, simplify=FALSE)
    [19-07-2023 12:40:12 UTC] R1: 162 sequence variants were inferred from 9005 input unique sequences. R2: 47 sequence variants were inferred from 16088 input unique sequences.
    [19-07-2023 12:40:13 UTC] mergePairs(dd$R1, derep$R1, dd$R2, derep$R2, verbose=TRUE, minOverlap=12, trimOverhang=FALSE, maxMismatch=0, justConcatenate=FALSE)
    [19-07-2023 12:40:13 UTC] 11701 paired-reads (in 85 unique pairings) successfully merged out of 15018 (in 267 pairings) input.
    [19-07-2023 12:40:13 UTC] seqtab <- makeSequenceTable(sampleVariants$sv)
    [19-07-2023 12:40:13 UTC] Removing sequences of length less than 75bp
    [19-07-2023 12:40:13 UTC] seqlengths <- nchar(colnames(seqtab))
    [19-07-2023 12:40:13 UTC] seqtab <- seqtab[,which(seqlengths >=75), drop=F]
    [19-07-2023 12:40:13 UTC] saveRDS(seqtab, file.path(interm.dir,"seqtab_min75.rds"))
    [19-07-2023 12:40:13 UTC] seqtabnochimera <- removeBimeraDenovo(seqtab, verbose=TRUE, multithread=12)
    [19-07-2023 12:40:13 UTC] Identified 568 bimeras out of 1349 input sequences.
    [19-07-2023 12:40:13 UTC] % Reads remaining after chimera removal: 71.4808330130532
    [19-07-2023 12:40:13 UTC] seqtab <- seqtabnochimera
    [19-07-2023 12:40:13 UTC] Track Reads
                 denoisedF denoisedR merged filter75 nochim
    [19-07-2023 12:40:13 UTC] A22831           20093     19494  14245    14245   7921
    [19-07-2023 12:40:13 UTC] A22833           18688     16924  10806    10806  10054
    [19-07-2023 12:40:13 UTC] A22349           19980     18528  12735    12735   8165
    [19-07-2023 12:40:13 UTC] A22192           20688     19840  17599    17599  13051
    [19-07-2023 12:40:13 UTC] A22187           20173     19243  17011    17011  10509
    [19-07-2023 12:40:13 UTC] A22061           19115     17917  14630    14630  12260
    [19-07-2023 12:40:13 UTC] A22057           20673     20147  16865    16865   9998
    [19-07-2023 12:40:13 UTC] A22145           17757     15789  12534    12534   9239
    [19-07-2023 12:40:13 UTC] A22350           18350     16709  12376    12376   9838
    [19-07-2023 12:40:13 UTC] 7pRecSw478.1     16806     15202  11701    11701   9397
    [19-07-2023 12:40:13 UTC] Saved Vega-Lite data to: /nephele_data/outputs/trackReadsVegaJSON.json
    [19-07-2023 12:40:13 UTC] rep_seq_names <- dada2fasta(seqtab, filename="/nephele_data/outputs/seq.fasta")
    [19-07-2023 12:40:13 UTC] rep_seq_names <- make_seq_names(seqtab, nametype)
    [19-07-2023 12:40:13 UTC] writeFasta(seqs, file="/nephele_data/outputs/seq.fasta")
    [19-07-2023 12:40:13 UTC] Taxonomic assignment with rdp
    [19-07-2023 12:40:17 UTC] taxa <- assignTaxonomy(seqtab, refdb, multithread=12, minBoot=80, tryRC=TRUE, verbose=TRUE)
    [19-07-2023 12:42:09 UTC] Finished processing reference fasta.
    [19-07-2023 12:42:09 UTC] Species assignment with dada2::addSpecies
    [19-07-2023 12:42:09 UTC] taxa.genus <- taxa; rm(taxa);
    [19-07-2023 12:42:13 UTC] taxa <- addSpecies(taxa.genus, refdb_species, verbose=TRUE, tryRC=TRUE, n=4000, allowMultiple =FALSE)
    [19-07-2023 12:43:28 UTC] 3 out of 781 were assigned to the species level.
    [19-07-2023 12:43:28 UTC] Of which 2 had genera consistent with the input table.Garbage collection 247 = 164+40+43 (level 2) ...
    [19-07-2023 12:43:28 UTC] 432.3 Mbytes of cons cells used (56%)
    [19-07-2023 12:43:28 UTC] 175.0 Mbytes of vectors used (5%)
    [19-07-2023 12:43:28 UTC] rep_seq_names <- make_seq_names(seqtab, nametype)
    [19-07-2023 12:43:28 UTC] writeFasta(seqs, file="/nephele_data/outputs/seq.fasta")
    [19-07-2023 12:43:28 UTC] colnames(seqtab) <- replace_names(colnames(seqtab), rep_seq_names)
    [19-07-2023 12:43:28 UTC] row.names(taxtab) <- replace_names(row.names(taxtab), rep_seq_names)
    [19-07-2023 12:43:30 UTC] write_biom(dada2biom(seqtab,taxtab, metadata = metadata), file.path(outdir, "taxa.biom"))
    [19-07-2023 12:43:30 UTC] dada2text(seqtab, taxtab, file.path(outdir, "OTU_table.txt"))
    [19-07-2023 12:43:30 UTC] dada2taxonomy(taxtab, file.path(outdir, "taxonomy_table.txt"))
    [19-07-2023 12:43:30 UTC] Garbage collection 248 = 164+40+44 (level 2) ...
    [19-07-2023 12:43:30 UTC] 432.1 Mbytes of cons cells used (56%)
    [19-07-2023 12:43:31 UTC] 111.6 Mbytes of vectors used (4%)
    [19-07-2023 12:43:31 UTC] Summarizing biom file to /nephele_data/outputs/otu_summary_table.txt.
    [19-07-2023 12:43:31 UTC] Creating phylogenetic trees
    [19-07-2023 12:43:33 UTC] Running command: mafft --preservecase --inputorder --thread 12 /nephele_data/outputs/seq.fasta > /nephele_data/outputs/phylo/aligned_seq.fasta
    [19-07-2023 12:43:37 UTC] Running command: FastTreeMP -quote -nt /nephele_data/outputs/phylo/aligned_seq.fasta > /nephele_data/outputs/phylo/unrooted_tree.nwk
    [19-07-2023 12:43:39 UTC] Finished creating trees: /nephele_data/outputs/phylo/rooted_tree.nwk, /nephele_data/outputs/phylo/unrooted_tree.nwk
    [19-07-2023 12:43:39 UTC] Checking output file from dada2 pipeline required by data visualization pipeline.
    [19-07-2023 12:43:39 UTC] Running data visualization pipeline
    [19-07-2023 12:43:43 UTC] Running with args: {'datafile': '/nephele_data/outputs/OTU_table.txt', 'outdir': '/nephele_data/outputs/', 'logfilename': '/var/log/job.log', 'sampdepth': 10054, 'mapfile': '/nephele_data/outputs/N2_16S_example_mapping_file_3_corrected.txt.no_gz', 'tsvfile': True}
    [19-07-2023 12:43:44 UTC] R version 4.3.1 (2023-06-16)
    [19-07-2023 12:43:44 UTC] Platform: x86_64-pc-linux-gnu (64-bit)
    [19-07-2023 12:43:44 UTC] Running under: Debian GNU/Linux 11 (bullseye)
    [19-07-2023 12:43:44 UTC] Matrix products: default
    [19-07-2023 12:43:44 UTC] BLAS:   /usr/lib/x86_64-linux-gnu/blas/libblas.so.3.9.0
    [19-07-2023 12:43:44 UTC] LAPACK: /usr/lib/x86_64-linux-gnu/lapack/liblapack.so.3.9.0
    [19-07-2023 12:43:44 UTC] locale:
     [1] LC_CTYPE=C.UTF-8       LC_NUMERIC=C           LC_TIME=C.UTF-8       
     [4] LC_COLLATE=C.UTF-8     LC_MONETARY=C.UTF-8    LC_MESSAGES=C.UTF-8   
     [7] LC_PAPER=C.UTF-8       LC_NAME=C              LC_ADDRESS=C
    [19-07-2023 12:43:44 UTC] [10] LC_TELEPHONE=C         LC_MEASUREMENT=C.UTF-8 LC_IDENTIFICATION=C
    [19-07-2023 12:43:44 UTC] time zone: America/New_York
    [19-07-2023 12:43:44 UTC] tzcode source: system (glibc)
    [19-07-2023 12:43:44 UTC] attached base packages:
    [19-07-2023 12:43:44 UTC] [1] stats     graphics  grDevices utils     datasets  methods   base
    [19-07-2023 12:43:44 UTC] other attached packages:
     [1] htmlwidgets_1.6.2 jsonlite_1.8.7    plotly_4.10.2     ampvis2_2.7.4    
     [5] ggplot2_3.4.2     vegan_2.6-4       lattice_0.20-45   permute_0.9-7    
     [9] htmltools_0.5.5   morpheus_0.1.1.1
    [19-07-2023 12:43:44 UTC] loaded via a namespace (and not attached):
     [1] Matrix_1.5-3       gtable_0.3.3       crayon_1.5.2       dplyr_1.1.2       
     [5] compiler_4.3.1     tidyselect_1.2.0   Rcpp_1.0.11        stringr_1.5.0     
     [9] parallel_4.3.1     tidyr_1.3.0        cluster_2.1.3      splines_4.3.1
    [19-07-2023 12:43:44 UTC] [13] scales_1.2.1       fastmap_1.1.1      plyr_1.8.8         R6_2.5.1
    [19-07-2023 12:43:44 UTC] [17] generics_0.1.3     MASS_7.3-58.3      ggrepel_0.9.3      tibble_3.2.1
    [19-07-2023 12:43:44 UTC] [21] munsell_0.5.0      pillar_1.9.0       RColorBrewer_1.1-3 rlang_1.1.1
    [19-07-2023 12:43:44 UTC] [25] utf8_1.2.3         stringi_1.7.12     lazyeval_0.2.2     viridisLite_0.4.2
    [19-07-2023 12:43:44 UTC] [29] cli_3.6.1          withr_2.5.0        magrittr_2.0.3     mgcv_1.8-42
    [19-07-2023 12:43:44 UTC] [33] digest_0.6.33      grid_4.3.1         lifecycle_1.0.3    nlme_3.1-162
    [19-07-2023 12:43:44 UTC] [37] vctrs_0.6.3        data.table_1.14.8  glue_1.6.2         ape_5.7-1
    [19-07-2023 12:43:44 UTC] [41] fansi_1.0.4        colorspace_2.1-0   purrr_1.0.1        httr_1.4.6
    [19-07-2023 12:43:44 UTC] [45] tools_4.3.1        pkgconfig_2.0.3
    [19-07-2023 12:43:44 UTC] "allgraphs"(datafile="/nephele_data/outputs/OTU_table.txt", outdir="/nephele_data/outputs//graphs", mapfile="/nephele_data/outputs/N2_16S_example_mapping_file_3_corrected.txt.no_gz",tsvfile=TRUE, ...)
    [19-07-2023 12:43:44 UTC] Reading in map file /nephele_data/outputs/N2_16S_example_mapping_file_3_corrected.txt.no_gz
    [19-07-2023 12:43:44 UTC] Reading in OTU file /nephele_data/outputs/OTU_table.txt
    [19-07-2023 12:43:44 UTC] otu <- read.delim(datafile, check.names = FALSE, na.strings = '', row.names = 1)
    [19-07-2023 12:43:44 UTC] tax <- otu[,!names(otu) %in% map$SampleID]
    [19-07-2023 12:43:44 UTC] otu <- otu[, names(otu) %in% map$SampleID, drop=F]
    [19-07-2023 12:43:44 UTC] otu <- cbind(otu, tax)
    [19-07-2023 12:43:44 UTC] amp <- amp_load(otu, map)
    [19-07-2023 12:43:45 UTC] Warning: Could not find a column named OTU/ASV in otutable, using rownames as sample ID's
    [19-07-2023 12:43:45 UTC] ampvis2 object with 3 elements.
    [19-07-2023 12:43:45 UTC] Summary of OTU table:
         Samples         OTUs  Total#Reads    Min#Reads    Max#Reads Median#Reads 
              10          781       100432         7921        13051         9918 
       Avg#Reads 
         10043.2
    [19-07-2023 12:43:45 UTC] Assigned taxonomy:
        Kingdom      Phylum       Class       Order      Family       Genus 
      781(100%) 771(98.72%) 770(98.59%) 760(97.31%) 702(89.88%) 527(67.48%) 
        Species 
       2(0.26%)
    [19-07-2023 12:43:45 UTC] Metadata variables: 7 
     SampleID, ForwardFastqFile, ReverseFastqFile, TreatmentGroup, Animal, Day, Description
    [19-07-2023 12:43:45 UTC] Rarefaction curve
    [19-07-2023 12:43:45 UTC] rarefactioncurve(outdir = outdir, amp = amp, colors = allcols, pipeline=TRUE)
    [19-07-2023 12:43:45 UTC] Warning in vegan::rarefy(abund[i, ], n) :
      most observed count data have counts 1, but smallest count is 8
    [19-07-2023 12:43:45 UTC] Warning in vegan::rarefy(abund[i, ], n) :
      most observed count data have counts 1, but smallest count is 9
    [19-07-2023 12:43:45 UTC] Warning in vegan::rarefy(abund[i, ], n) :
      most observed count data have counts 1, but smallest count is 4
    [19-07-2023 12:43:45 UTC] Warning in vegan::rarefy(abund[i, ], n) :
      most observed count data have counts 1, but smallest count is 4
    [19-07-2023 12:43:45 UTC] Warning in vegan::rarefy(abund[i, ], n) :
      most observed count data have counts 1, but smallest count is 24
    [19-07-2023 12:43:45 UTC] Warning in vegan::rarefy(abund[i, ], n) :
      most observed count data have counts 1, but smallest count is 9
    [19-07-2023 12:43:45 UTC] Warning in vegan::rarefy(abund[i, ], n) :
      most observed count data have counts 1, but smallest count is 6
    [19-07-2023 12:43:45 UTC] Warning in vegan::rarefy(abund[i, ], n) :
      most observed count data have counts 1, but smallest count is 7
    [19-07-2023 12:43:45 UTC] Warning in vegan::rarefy(abund[i, ], n) :
      most observed count data have counts 1, but smallest count is 2
    [19-07-2023 12:43:45 UTC] Warning in vegan::rarefy(abund[i, ], n) :
      most observed count data have counts 1, but smallest count is 30
    [19-07-2023 12:43:45 UTC] Saving plot to /nephele_data/outputs/graphs/rarecurve.html
    [19-07-2023 12:43:46 UTC] Warning in plotly::config(pp, cloud = T, edits = list(titleText = T, legendText = T,  :
      The `cloud` argument is deprecated. Use `showSendToCloud` instead.
    [19-07-2023 12:43:46 UTC] Saving rarefaction curve table to /nephele_data/outputs//graphs/rarecurve.txt
    [19-07-2023 12:43:46 UTC] Relative abundance heatmaps
    [19-07-2023 12:43:46 UTC] morphheatmap(outdir = outdir, amp = amp, colors=allcols, filter_level = 5)
    [19-07-2023 12:43:46 UTC] Filter taxa below 5 counts/abundance.
    [19-07-2023 12:43:46 UTC] amp <- filterlowabund(amp, level = 5, abs=T)
    [19-07-2023 12:43:46 UTC] Calculate relative abundance.
    [19-07-2023 12:43:46 UTC] amp <- subsetamp(amp, sampdepth = NULL, rarefy=FALSE, normalise = TRUE, printsummary = FALSE)
    [19-07-2023 12:43:46 UTC] 0 samples have been filtered.
    [19-07-2023 12:43:46 UTC] makeheatmap("seq", amp)
    [19-07-2023 12:43:48 UTC] heatmap <- morpheus(mat, columns=columns, columnAnnotations = amptax$metadata, columnColorModel = list(type=as.list(colors)), colorScheme = list(scalingMode="fixed", values=values, colors=hmapcolors, stepped=FALSE), rowAnnotations = amptax$tax, rows = rows, dendrogram="none")
    [19-07-2023 12:43:48 UTC] Saving plot to /nephele_data/outputs/graphs/seq_heatmap.html
    [19-07-2023 12:43:48 UTC] Sampling depth: 10054
    [19-07-2023 12:43:48 UTC] Filter samples below 10054 counts.
    [19-07-2023 12:43:48 UTC] amp <- amp_subset_samples(amp, minreads = 10054, ...)
    [19-07-2023 12:43:48 UTC] 6 samples and 448 OTUs have been filtered
    [19-07-2023 12:43:48 UTC] Before: 10 samples and 781 OTUs
    [19-07-2023 12:43:48 UTC] After: 4 samples and 333 OTUs
    [19-07-2023 12:43:48 UTC] Saving excluded sample ids to /nephele_data/outputs//graphs/samples_being_ignored.txt
    [19-07-2023 12:43:48 UTC] ampvis2 object with 3 elements.
    [19-07-2023 12:43:48 UTC] Summary of OTU table:
         Samples         OTUs  Total#Reads    Min#Reads    Max#Reads Median#Reads 
               4          333        45874        10054        13051      11384.5 
       Avg#Reads 
         11468.5
    [19-07-2023 12:43:48 UTC] Assigned taxonomy:
        Kingdom      Phylum       Class       Order      Family       Genus 
      333(100%)  330(99.1%)  330(99.1%)  320(96.1%) 296(88.89%) 227(68.17%) 
        Species 
        2(0.6%)
    [19-07-2023 12:43:48 UTC] Metadata variables: 7 
     SampleID, ForwardFastqFile, ReverseFastqFile, TreatmentGroup, Animal, Day, Description
    [19-07-2023 12:43:48 UTC] PCoA plot with binomial distance
    [19-07-2023 12:43:48 UTC] pcoaplot(outdir = outdir, amp = ampsub, distm = "binomial", colors = allcols)
    [19-07-2023 12:43:49 UTC] pcoa <- amp_ordinate(amp, filter_species =0.1,type="PCOA", distmeasure ="binomial",sample_color_by = "TreatmentGroup", detailed_output = TRUE, transform="none")
    [19-07-2023 12:43:49 UTC] Saving plot to /nephele_data/outputs/graphs/pcoa_binomial.html
    [19-07-2023 12:43:49 UTC] Warning in plotly::config(pp, cloud = T, edits = list(titleText = T, legendText = T,  :
      The `cloud` argument is deprecated. Use `showSendToCloud` instead.
    [19-07-2023 12:43:49 UTC] Saving binomial PCoA table to /nephele_data/outputs//graphs/pcoa_binomial.txt
    [19-07-2023 12:43:49 UTC] Making top species table.
    [19-07-2023 12:43:49 UTC] Saving table to /nephele_data/outputs//graphs/top_85_species_table.txt
    [19-07-2023 12:43:49 UTC] Rarefying OTU Table to  10054 reads.
    [19-07-2023 12:43:49 UTC] set.seed(500)
    [19-07-2023 12:43:49 UTC] otu <- rrarefy(t(amp$abund), sampdepth)
    [19-07-2023 12:43:49 UTC] Warning in rrarefy(t(amp$abund), sampdepth) :
      function should be used for observed counts, but smallest count is 4
    [19-07-2023 12:43:49 UTC] amp <- amp_subset_samples(amp, minreads = 10054, ...)
    [19-07-2023 12:43:49 UTC] 0 samples have been filtered.
    [19-07-2023 12:43:49 UTC] ampvis2 object with 3 elements.
    [19-07-2023 12:43:49 UTC] Summary of OTU table:
         Samples         OTUs  Total#Reads    Min#Reads    Max#Reads Median#Reads 
               4          333        40216        10054        10054        10054 
       Avg#Reads 
           10054
    [19-07-2023 12:43:49 UTC] Assigned taxonomy:
        Kingdom      Phylum       Class       Order      Family       Genus 
      333(100%)  330(99.1%)  330(99.1%)  320(96.1%) 296(88.89%) 227(68.17%) 
        Species 
        2(0.6%)
    [19-07-2023 12:43:49 UTC] Metadata variables: 7 
     SampleID, ForwardFastqFile, ReverseFastqFile, TreatmentGroup, Animal, Day, Description
    [19-07-2023 12:43:49 UTC] Saving rarefied OTU Table to  /nephele_data/outputs//graphs/rarefied_OTU_table_10054.txt
    [19-07-2023 12:43:49 UTC] Making heatmap from rarefied counts.
    [19-07-2023 12:43:49 UTC] morphheatmap(outdir = outdir, amp = amprare, colors=allcols, filter_level = 5, filesuffix = "_rarefied")
    [19-07-2023 12:43:49 UTC] Filter taxa below 5 counts/abundance.
    [19-07-2023 12:43:49 UTC] amp <- filterlowabund(amp, level = 5, abs=T)
    [19-07-2023 12:43:49 UTC] Calculate relative abundance.
    [19-07-2023 12:43:49 UTC] amp <- subsetamp(amp, sampdepth = NULL, rarefy=FALSE, normalise = TRUE, printsummary = FALSE)
    [19-07-2023 12:43:49 UTC] 0 samples have been filtered.
    [19-07-2023 12:43:49 UTC] makeheatmap("seq", amp)
    [19-07-2023 12:43:49 UTC] heatmap <- morpheus(mat, columns=columns, columnAnnotations = amptax$metadata, columnColorModel = list(type=as.list(colors)), colorScheme = list(scalingMode="fixed", values=values, colors=hmapcolors, stepped=FALSE), rowAnnotations = amptax$tax, rows = rows, dendrogram="none")
    [19-07-2023 12:43:49 UTC] Saving plot to /nephele_data/outputs/graphs/seq_heatmap_rarefied.html
    [19-07-2023 12:43:49 UTC] Normalizing rarefied OTU table to 100 for Bray-Curtis distance.
    [19-07-2023 12:43:49 UTC] 0 samples have been filtered.
    [19-07-2023 12:43:49 UTC] pcoaplot(outdir = outdir, amp = ampbc, distm = "bray", colors = allcols, filesuffix="_rarefied")
    [19-07-2023 12:43:49 UTC] pcoa <- amp_ordinate(amp, filter_species =0.1,type="PCOA", distmeasure ="bray",sample_color_by = "TreatmentGroup", detailed_output = TRUE, transform="none")
    [19-07-2023 12:43:49 UTC] Saving plot to /nephele_data/outputs/graphs/pcoa_bray_rarefied.html
    [19-07-2023 12:43:49 UTC] Warning in plotly::config(pp, cloud = T, edits = list(titleText = T, legendText = T,  :
      The `cloud` argument is deprecated. Use `showSendToCloud` instead.
    [19-07-2023 12:43:49 UTC] Saving bray PCoA table to /nephele_data/outputs//graphs/pcoa_bray_rarefied.txt
    [19-07-2023 12:43:49 UTC] Alpha diversity boxplot
    [19-07-2023 12:43:49 UTC] adivboxplot(outdir = outdir, amp = amprare, sampdepth = sampdepth, colors = allcols, pipeline=TRUE)
    [19-07-2023 12:43:49 UTC] alphadiv <- amp_alphadiv(amp, measure="shannon", richness = TRUE, rarefy = 10054)
    [19-07-2023 12:43:49 UTC] Warning: The data you have provided does not have
    [19-07-2023 12:43:49 UTC] any singletons. This is highly suspicious. Results of richness
    [19-07-2023 12:43:49 UTC] estimates (for example) are probably unreliable, or wrong, if you have already
    [19-07-2023 12:43:49 UTC] trimmed low-abundance taxa from the data.
    [19-07-2023 12:43:49 UTC] We recommend that you find the un-trimmed data and retry.
    [19-07-2023 12:43:50 UTC] Saving alpha diversity table to /nephele_data/outputs//graphs/alphadiv.txt
    [19-07-2023 12:43:50 UTC] Saving plot to /nephele_data/outputs/graphs/alphadiv.html
    [19-07-2023 12:43:50 UTC] Warning in plotly::config(pp, cloud = T, edits = list(titleText = T, legendText = T,  :
      The `cloud` argument is deprecated. Use `showSendToCloud` instead.
    [19-07-2023 12:43:51 UTC] "allgraphs" complete.
    [19-07-2023 12:43:51 UTC] Result 'ref_db' reported
    [19-07-2023 12:43:51 UTC] Result 'error_rate_r1' reported
    [19-07-2023 12:43:51 UTC] Result 'rooted_tree' reported
    [19-07-2023 12:43:51 UTC] Result 'top_species_table' reported
    [19-07-2023 12:43:51 UTC] Result 'track_reads' reported
    [19-07-2023 12:43:51 UTC] Result 'sampling_depth' reported
    [19-07-2023 12:43:51 UTC] Result 'otu_summary_table' reported
    [19-07-2023 12:43:51 UTC] Result 'biom' reported
    [19-07-2023 12:43:51 UTC] Result 'alphadiv' reported
    [19-07-2023 12:43:51 UTC] Result 'pcoa_binomial' reported
    [19-07-2023 12:43:51 UTC] Result 'rarecurve' reported
    [19-07-2023 12:43:51 UTC] Result 'logfile_debug' reported
    [19-07-2023 12:43:51 UTC] Result 'quality_profile_r2' reported
    [19-07-2023 12:43:51 UTC] Result 'error_rate_r2' reported
    [19-07-2023 12:43:51 UTC] Result 'pcoa_bray' reported
    [19-07-2023 12:43:51 UTC] Result 'otu_table' reported
    [19-07-2023 12:43:51 UTC] Optional result 'species_heatmap' does not exist: /nephele_data/outputs/graphs/Species_heatmap.html
    [19-07-2023 12:43:51 UTC] Result 'rarefied_otu_table' reported
    [19-07-2023 12:43:51 UTC] Result 'seq_fasta' reported
    [19-07-2023 12:43:51 UTC] Result 'quality_profile_r1' reported
    [19-07-2023 12:43:51 UTC] Result 'taxonomy_table' reported
    [19-07-2023 12:43:51 UTC] Result 'reads_in_reads_out' reported
    [19-07-2023 12:43:51 UTC] Result 'seq_heatmap' reported
    [19-07-2023 12:43:51 UTC] Result 'taxmethod' reported
    [19-07-2023 12:43:52 UTC] Results tarball does not exist: /mnt/EFS/user_uploads/b73de8bfdd22_reported_results.tar.gz. Creating.
    [19-07-2023 12:43:52 UTC] Created results tarball: /mnt/EFS/user_uploads/b73de8bfdd22_reported_results.tar.gz
    [19-07-2023 12:43:52 UTC] Uploaded to S3: /mnt/EFS/user_uploads/b73de8bfdd22_reported_results.tar.gz
    [19-07-2023 12:43:52 UTC] Uploaded to S3: /mnt/EFS/user_uploads/b73de8bfdd22/outputs/b73de8bfdd22_results_registry.json
    [19-07-2023 12:43:52 UTC] DADA2 pipeline complete.
    [19-07-2023 12:43:56 UTC] None

