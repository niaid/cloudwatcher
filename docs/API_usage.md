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

```




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




    {'RequestId': 'c4057a5f-4aac-4231-9e9c-4c171b9b0ef1',
     'HTTPStatusCode': 200,
     'HTTPHeaders': {'x-amzn-requestid': 'c4057a5f-4aac-4231-9e9c-4c171b9b0ef1',
      'content-type': 'text/xml',
      'content-length': '1596',
      'date': 'Thu, 26 Jan 2023 16:51:57 GMT'},
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





    [487075840.0,
     3613966336.0,
     5853335552.0,
     5131206656.0,
     5107838976.0,
     3095851008.0,
     2578575360.0,
     2525331456.0,
     2160402432.0]



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




    LogEventsList(events=[LogEvent(message='[2023-01-11 10:50:47,354 - INFO] Nephele, developed by BCBB/OCICB/NIAID/NIH version: 2.21.8, tag: Nephele_2022_December_22, commit: caa66b1', timestamp=datetime.datetime(2023, 1, 11, 10, 50, 48, 277000)), LogEvent(message='[2023-01-11 10:50:47,354 - INFO] Python version: 3.8.13', timestamp=datetime.datetime(2023, 1, 11, 10, 50, 48, 277000))], next_forward_token='f/37319232190733584015059832158212944362474954267242725377/s', next_backward_token='b/37319232190733584015059832158212944362474954267242725376/s')



The log events are returned as a custom `LogEventsList` object, which conists of a list of `LogEvents` and tokens. The next token (`LogEventsList.next_forward_token`) can be used to get the next batch of log events. The token can be provided to the `LogWatcher` constructor to start streaming from the last event.

### Retrieving all logs

Alternatively, the `return_formatted_logs` method can be used to retrieve all the logs. This method returns a `Tuple[str,str]`, where the first element is the formatted log and the second element is the next token. 


```python
formatted_logs, token = lw.return_formatted_logs()

print(formatted_logs)

```

    [11-01-2023 10:50:48 UTC] Nephele, developed by BCBB/OCICB/NIAID/NIH version: 2.21.8, tag: Nephele_2022_December_22, commit: caa66b1
    [11-01-2023 10:50:48 UTC] Python version: 3.8.13
    [11-01-2023 10:50:48 UTC] Current time: 2023-01-11 10:50
    [11-01-2023 10:50:48 UTC] Pipeline name: DADA2
    [11-01-2023 10:50:48 UTC] Job Description: test
    [11-01-2023 10:50:48 UTC] Job parameters
    [11-01-2023 10:50:48 UTC] job_id: d5b6be48d21e
    [11-01-2023 10:50:48 UTC] inputs_dir: None
    [11-01-2023 10:50:48 UTC] outputs_dir: None
    [11-01-2023 10:50:48 UTC] map_file: <_io.TextIOWrapper name='/nephele_data/inputs/N2_16S_example_mapping_file_min_corrected.txt' mode='r' encoding='UTF-8'>
    [11-01-2023 10:50:48 UTC] data_type: PE
    [11-01-2023 10:50:48 UTC] wurlitzer_stdout: file
    [11-01-2023 10:50:48 UTC] wurlitzer_stderr: file
    [11-01-2023 10:50:48 UTC] ion_torrent: False
    [11-01-2023 10:50:48 UTC] trimleft_fwd: 0
    [11-01-2023 10:50:48 UTC] trimleft_rev: 0
    [11-01-2023 10:50:48 UTC] maxee: 5
    [11-01-2023 10:50:48 UTC] trunclen_fwd: 0
    [11-01-2023 10:50:48 UTC] trunclen_rev: 0
    [11-01-2023 10:50:48 UTC] truncq: 4
    [11-01-2023 10:50:48 UTC] just_concatenate: False
    [11-01-2023 10:50:48 UTC] maxmismatch: 0
    [11-01-2023 10:50:48 UTC] trim_overhang: False
    [11-01-2023 10:50:48 UTC] chimera: True
    [11-01-2023 10:50:48 UTC] ref_db: sv138.1
    [11-01-2023 10:50:48 UTC] taxmethod: rdp
    [11-01-2023 10:50:48 UTC] sampling_depth: None
    [11-01-2023 10:50:48 UTC] Checking Mapfile for Gzipped inputs.
    [11-01-2023 10:50:48 UTC] Gzipped files listed in map file, attempting to rm .gz extension.
    [11-01-2023 10:50:48 UTC] Done. Attempting file decompression.
    [11-01-2023 10:50:53 UTC] Finished decompression.
    [11-01-2023 10:51:02 UTC] Reference DB (sv138.1) checksum: 6b41db7139834c71171f8ce5b5918fc6
    [11-01-2023 10:51:04 UTC] Taxonomy assignemnt DB checksum: f21c2d97c79ff07c17949a9622371a4c
    [11-01-2023 10:51:09 UTC] Loading R module: DADA2/dada2nephele.
    [11-01-2023 10:51:36 UTC] Running DADA2.
    [11-01-2023 10:51:39 UTC] R version 4.1.3 (2022-03-10)
    [11-01-2023 10:51:39 UTC] Platform: x86_64-conda-linux-gnu (64-bit)
    [11-01-2023 10:51:39 UTC] Running under: Debian GNU/Linux 11 (bullseye)
    [11-01-2023 10:51:39 UTC] Matrix products: default
    [11-01-2023 10:51:39 UTC] BLAS/LAPACK: /usr/local/bin/miniconda3/envs/qiime2-2022.2/lib/libopenblasp-r0.3.20.so
    [11-01-2023 10:51:39 UTC] locale:
     [1] LC_CTYPE=C.UTF-8       LC_NUMERIC=C           LC_TIME=C.UTF-8       
     [4] LC_COLLATE=C.UTF-8     LC_MONETARY=C.UTF-8    LC_MESSAGES=C.UTF-8   
     [7] LC_PAPER=C.UTF-8       LC_NAME=C              LC_ADDRESS=C
    [11-01-2023 10:51:39 UTC] [10] LC_TELEPHONE=C         LC_MEASUREMENT=C.UTF-8 LC_IDENTIFICATION=C
    [11-01-2023 10:51:39 UTC] attached base packages:
    [11-01-2023 10:51:39 UTC] [1] tools     stats     graphics  grDevices utils     datasets  methods
    [11-01-2023 10:51:39 UTC] [8] base
    [11-01-2023 10:51:39 UTC] other attached packages:
    [11-01-2023 10:51:39 UTC] [1] dada2nephele_0.1.2
    [11-01-2023 10:51:39 UTC] loaded via a namespace (and not attached):
     [1] Rcpp_1.0.8.3                lattice_0.20-45            
     [3] png_0.1-7                   Rsamtools_2.10.0           
     [5] Biostrings_2.62.0           foreach_1.5.2              
     [7] digest_0.6.29               utf8_1.2.2                 
     [9] R6_2.5.1                    GenomeInfoDb_1.30.0
    [11-01-2023 10:51:39 UTC] [11] plyr_1.8.7                  ShortRead_1.52.0
    [11-01-2023 10:51:39 UTC] [13] stats4_4.1.3                RSQLite_2.2.8
    [11-01-2023 10:51:39 UTC] [15] ggplot2_3.3.6               pillar_1.7.0
    [11-01-2023 10:51:39 UTC] [17] zlibbioc_1.40.0             rlang_1.0.2
    [11-01-2023 10:51:39 UTC] [19] blob_1.2.3                  S4Vectors_0.32.3
    [11-01-2023 10:51:39 UTC] [21] Matrix_1.4-1                BiocParallel_1.28.3
    [11-01-2023 10:51:39 UTC] [23] stringr_1.4.0               dada2_1.22.0
    [11-01-2023 10:51:39 UTC] [25] RCurl_1.98-1.6              bit_4.0.4
    [11-01-2023 10:51:39 UTC] [27] munsell_0.5.0               DelayedArray_0.20.0
    [11-01-2023 10:51:39 UTC] [29] compiler_4.1.3              pkgconfig_2.0.3
    [11-01-2023 10:51:39 UTC] [31] BiocGenerics_0.40.0         biomformat_1.22.0
    [11-01-2023 10:51:39 UTC] [33] tidyselect_1.1.2            SummarizedExperiment_1.24.0
    [11-01-2023 10:51:39 UTC] [35] tibble_3.1.7                GenomeInfoDbData_1.2.7
    [11-01-2023 10:51:39 UTC] [37] codetools_0.2-18            IRanges_2.28.0
    [11-01-2023 10:51:39 UTC] [39] matrixStats_0.62.0          fansi_1.0.3
    [11-01-2023 10:51:39 UTC] [41] crayon_1.5.1                dplyr_1.0.9
    [11-01-2023 10:51:39 UTC] [43] rhdf5filters_1.6.0          GenomicAlignments_1.30.0
    [11-01-2023 10:51:39 UTC] [45] bitops_1.0-7                grid_4.1.3
    [11-01-2023 10:51:39 UTC] [47] jsonlite_1.8.0              gtable_0.3.0
    [11-01-2023 10:51:39 UTC] [49] lifecycle_1.0.1             DBI_1.1.2
    [11-01-2023 10:51:39 UTC] [51] magrittr_2.0.3              scales_1.2.0
    [11-01-2023 10:51:39 UTC] [53] RcppParallel_5.1.5          cachem_1.0.6
    [11-01-2023 10:51:39 UTC] [55] cli_3.3.0                   stringi_1.7.6
    [11-01-2023 10:51:39 UTC] [57] XVector_0.34.0              hwriter_1.3.2.1
    [11-01-2023 10:51:39 UTC] [59] reshape2_1.4.4              latticeExtra_0.6-29
    [11-01-2023 10:51:39 UTC] [61] ellipsis_0.3.2              generics_0.1.2
    [11-01-2023 10:51:39 UTC] [63] vctrs_0.4.1                 Rhdf5lib_1.16.0
    [11-01-2023 10:51:39 UTC] [65] RColorBrewer_1.1-3          DECIPHER_2.22.0
    [11-01-2023 10:51:39 UTC] [67] iterators_1.0.14            bit64_4.0.5
    [11-01-2023 10:51:39 UTC] [69] Biobase_2.54.0              glue_1.6.2
    [11-01-2023 10:51:39 UTC] [71] purrr_0.3.4                 MatrixGenerics_1.6.0
    [11-01-2023 10:51:39 UTC] [73] jpeg_0.1-9                  fastmap_1.1.0
    [11-01-2023 10:51:39 UTC] [75] parallel_4.1.3              rhdf5_2.38.0
    [11-01-2023 10:51:39 UTC] [77] colorspace_2.0-3            GenomicRanges_1.46.1
    [11-01-2023 10:51:39 UTC] [79] memoise_2.0.1
    [11-01-2023 10:51:39 UTC] Taxonomic Reference Database
    [11-01-2023 10:51:39 UTC] /mnt/EFS/dbs/dada2_silva_v138.1/silva_nr99_v138.1_train_set.fa.gz
    [11-01-2023 10:51:39 UTC] /mnt/EFS/dbs/dada2_silva_v138.1/silva_species_assignment_v138.1.fa.gz
    [11-01-2023 10:51:39 UTC] Reading in map file  /nephele_data/outputs/N2_16S_example_mapping_file_min_corrected.txt.no_gz
    [11-01-2023 10:51:39 UTC] Printing dada algorithm options.
                  BAND_SIZE       DETECT_SINGLETONS             GAP_PENALTY 
                         16                   FALSE                      -8 
                    GAPLESS                  GREEDY HOMOPOLYMER_GAP_PENALTY 
                       TRUE                    TRUE                    NULL 
               KDIST_CUTOFF                   MATCH               MAX_CLUST 
                       0.42                       5                       0 
                MAX_CONSIST           MIN_ABUNDANCE                MIN_FOLD 
                         10                       1                       1 
                MIN_HAMMING                MISMATCH                 OMEGA_A 
                          1                      -4                   1e-40 
                    OMEGA_C                 OMEGA_P        PSEUDO_ABUNDANCE 
                      1e-40                   1e-04                     Inf 
          PSEUDO_PREVALENCE                     SSE               USE_KMERS 
                          2                       2                    TRUE 
                  USE_QUALS    VECTORIZED_ALIGNMENT 
                       TRUE                    TRUE
    [11-01-2023 10:51:39 UTC] Paired End
    [11-01-2023 10:51:44 UTC] out <- filterAndTrim(fwd=file.path(datadir,readslist$R1), filt=file.path(filt.dir,trimlist$R1),rev=file.path(datadir,readslist$R2), filt.rev=file.path(filt.dir,trimlist$R2),  maxEE=5L, trimLeft=list(0L, 0L), truncQ=4, truncLen = list(0L, 0L), rm.phix=TRUE, compress=TRUE, verbose=TRUE, multithread=FALSE, minLen=50, OMP = FALSE)
    [11-01-2023 10:51:49 UTC] reads.in reads.out
    [11-01-2023 10:51:49 UTC] 22061_S5_R1_subsample.fastq    25000     20200
    [11-01-2023 10:51:49 UTC] 22057_S2_R1_subsample.fastq    25000     20969
    [11-01-2023 10:51:49 UTC] Checking that trimmed files exist.
    [11-01-2023 10:51:49 UTC] list2env(checktrimfiles(A, filt.dir, trimlist), envir = environment())
    [11-01-2023 10:51:50 UTC] err <- lapply(trimlist, function(x) learnErrors(x, multithread=nthread, nbases=100000000,randomize=FALSE))
    [11-01-2023 10:51:55 UTC] 10744514 total bases in 41169 reads from 2 samples will be used for learning the error rates.
    [11-01-2023 10:52:05 UTC] 10716719 total bases in 41169 reads from 2 samples will be used for learning the error rates.
    [11-01-2023 10:52:19 UTC] pe <- lapply(err, function(x) plotErrors(x, nominalQ=TRUE))
    [11-01-2023 10:52:20 UTC] derep <- lapply(trimlist, function(x) derepFastq(x[sample], verbose=TRUE))
    [11-01-2023 10:52:22 UTC] dd <- sapply(nameslist, function(x) dada(derep[[x]], err=err[[x]], multithread=nthread, verbose=F), USE.NAMES=TRUE, simplify=FALSE)
    [11-01-2023 10:52:22 UTC] R1: 191 sequence variants were inferred from 11283 input unique sequences. R2: 78 sequence variants were inferred from 17350 input unique sequences.
    [11-01-2023 10:52:22 UTC] mergePairs(dd$R1, derep$R1, dd$R2, derep$R2, verbose=TRUE, minOverlap=12, trimOverhang=FALSE, maxMismatch=0, justConcatenate=FALSE)
    [11-01-2023 10:52:24 UTC] derep <- lapply(trimlist, function(x) derepFastq(x[sample], verbose=TRUE))
    [11-01-2023 10:52:25 UTC] dd <- sapply(nameslist, function(x) dada(derep[[x]], err=err[[x]], multithread=nthread, verbose=F), USE.NAMES=TRUE, simplify=FALSE)
    [11-01-2023 10:52:25 UTC] R1: 145 sequence variants were inferred from 9268 input unique sequences. R2: 132 sequence variants were inferred from 15736 input unique sequences.
    [11-01-2023 10:52:26 UTC] mergePairs(dd$R1, derep$R1, dd$R2, derep$R2, verbose=TRUE, minOverlap=12, trimOverhang=FALSE, maxMismatch=0, justConcatenate=FALSE)
    [11-01-2023 10:52:26 UTC] seqtab <- makeSequenceTable(sampleVariants$sv)
    [11-01-2023 10:52:26 UTC] Removing sequences of length less than 75bp
    [11-01-2023 10:52:26 UTC] seqlengths <- nchar(colnames(seqtab))
    [11-01-2023 10:52:26 UTC] seqtab <- seqtab[,which(seqlengths >=75), drop=F]
    [11-01-2023 10:52:26 UTC] saveRDS(seqtab, file.path(interm.dir,"seqtab_min75.rds"))
    [11-01-2023 10:52:26 UTC] seqtabnochimera <- removeBimeraDenovo(seqtab, verbose=TRUE, multithread=nthread)
    [11-01-2023 10:52:26 UTC] % Reads remaining after chimera removal: 73.7906665042037
    [11-01-2023 10:52:26 UTC] seqtab <- seqtabnochimera
    [11-01-2023 10:52:26 UTC] Track Reads
           denoisedF denoisedR merged filter75 nochim
    [11-01-2023 10:52:26 UTC] A22061     18991     17776  14559    14559  12339
    [11-01-2023 10:52:26 UTC] A22057     20661     20123  18269    18269  11885
    [11-01-2023 10:52:26 UTC] rep_seq_names <- make_seq_names(seqtab)
    [11-01-2023 10:52:26 UTC] writeFasta(seqs, file=file.path(outdir, "seq.fasta"))
    [11-01-2023 10:52:26 UTC] Taxonomic assignment with rdp
    [11-01-2023 10:52:31 UTC] taxa <- assignTaxonomy(seqtab, refdb, multithread=nthread, minBoot=80, tryRC=TRUE, verbose=TRUE)
    [11-01-2023 10:54:30 UTC] Finished processing reference fasta.
    [11-01-2023 10:54:34 UTC] taxa.species <- addSpecies(taxa, refdb_species, verbose=TRUE, tryRC=TRUE, n=4000)
    [11-01-2023 10:55:19 UTC] 0 out of 214 were assigned to the species level.
    [11-01-2023 10:55:19 UTC] Of which 0 had genera consistent with the input table.
    [11-01-2023 10:55:19 UTC] otu_tab <- seqtab; colnames(otu_tab) <- replace_names(colnames(otu_tab), rep_seq_names)
    [11-01-2023 10:55:19 UTC] row.names(taxa.species) <- replace_names(row.names(taxa.species), rep_seq_names)
    [11-01-2023 10:55:19 UTC] write_biom(dada2biom(otu_tab,taxa.species, metadata = A), file.path(outdir, "taxa.biom"))
    [11-01-2023 10:55:19 UTC] dada2text(otu_tab, taxa.species, file.path(outdir, "OTU_table.txt"))
    [11-01-2023 10:55:20 UTC] dada2taxonomy(taxa.species, file.path(outdir, "taxonomy_table.txt"))
    [11-01-2023 10:55:20 UTC] Summarizing biom file to /nephele_data/outputs/otu_summary_table.txt.
    [11-01-2023 10:55:20 UTC] Creating a phylogenetic tree with 12 threads
    [11-01-2023 10:55:20 UTC] phylogeny version 2022.2.0. This QIIME 2 plugin supports generating and manipulating phylogenetic trees.
    [11-01-2023 10:55:20 UTC] Artifact.import_data(type='FeatureData[Sequence]', view=/nephele_data/outputs/seq.fasta)
    [11-01-2023 10:55:23 UTC] align_to_tree_mafft_fasttree(sequences=seqs, n_threads=num_threads)
    [11-01-2023 10:55:23 UTC] Saving trees to /nephele_data/outputs/phylo
    [11-01-2023 10:55:23 UTC] Checking output file from dada2 pipeline required by data visualization pipeline.
    [11-01-2023 10:55:23 UTC] 2 samples are above the sampling depth of 10000, which is insufficient.  At least 3 are needed.
    [11-01-2023 10:55:27 UTC] Loading R module: datavis16s.
    [11-01-2023 10:55:32 UTC] Running data visualization pipeline.
    [11-01-2023 10:55:32 UTC] R version 4.1.3 (2022-03-10)
    [11-01-2023 10:55:32 UTC] Platform: x86_64-conda-linux-gnu (64-bit)
    [11-01-2023 10:55:32 UTC] Running under: Debian GNU/Linux 11 (bullseye)
    [11-01-2023 10:55:32 UTC] Matrix products: default
    [11-01-2023 10:55:32 UTC] BLAS/LAPACK: /usr/local/bin/miniconda3/envs/qiime2-2022.2/lib/libopenblasp-r0.3.20.so
    [11-01-2023 10:55:32 UTC] locale:
    [11-01-2023 10:55:32 UTC] [1] C.UTF-8
    [11-01-2023 10:55:32 UTC] attached base packages:
    [11-01-2023 10:55:32 UTC] [1] tools     stats     graphics  grDevices utils     datasets  methods
    [11-01-2023 10:55:32 UTC] [8] base
    [11-01-2023 10:55:32 UTC] other attached packages:
    [11-01-2023 10:55:32 UTC] [1] datavis16s_0.1.3   dada2nephele_0.1.2
    [11-01-2023 10:55:32 UTC] loaded via a namespace (and not attached):
      [1] nlme_3.1-157                bitops_1.0-7               
      [3] matrixStats_0.62.0          bit64_4.0.5                
      [5] RColorBrewer_1.1-3          httr_1.4.3                 
      [7] GenomeInfoDb_1.30.0         utf8_1.2.2                 
      [9] R6_2.5.1                    vegan_2.6-2                
     [11] mgcv_1.8-40                 DBI_1.1.2                  
     [13] BiocGenerics_0.40.0         lazyeval_0.2.2             
     [15] colorspace_2.0-3            permute_0.9-7              
     [17] rhdf5filters_1.6.0          tidyselect_1.1.2           
     [19] bit_4.0.4                   compiler_4.1.3             
     [21] cli_3.3.0                   Biobase_2.54.0             
     [23] DelayedArray_0.20.0         plotly_4.10.0              
     [25] labeling_0.4.2              scales_1.2.0               
     [27] stringr_1.4.0               digest_0.6.29              
     [29] Rsamtools_2.10.0            dada2_1.22.0               
     [31] XVector_0.34.0              jpeg_0.1-9                 
     [33] pkgconfig_2.0.3             htmltools_0.5.2            
     [35] MatrixGenerics_1.6.0        fastmap_1.1.0              
     [37] htmlwidgets_1.5.4           rlang_1.0.2                
     [39] RSQLite_2.2.8               farver_2.1.0               
     [41] generics_0.1.2              hwriter_1.3.2.1            
     [43] jsonlite_1.8.0              BiocParallel_1.28.3        
     [45] dplyr_1.0.9                 RCurl_1.98-1.6             
     [47] magrittr_2.0.3              GenomeInfoDbData_1.2.7     
     [49] biomformat_1.22.0           Matrix_1.4-1               
     [51] Rcpp_1.0.8.3                munsell_0.5.0              
     [53] S4Vectors_0.32.3            Rhdf5lib_1.16.0            
     [55] fansi_1.0.3                 DECIPHER_2.22.0            
     [57] ape_5.6-2                   lifecycle_1.0.1            
     [59] stringi_1.7.6               ampvis2_2.7.4              
     [61] MASS_7.3-57                 SummarizedExperiment_1.24.0
     [63] zlibbioc_1.40.0             rhdf5_2.38.0               
     [65] plyr_1.8.7                  grid_4.1.3                 
     [67] blob_1.2.3                  parallel_4.1.3             
     [69] ggrepel_0.9.1               crayon_1.5.1               
     [71] lattice_0.20-45             splines_4.1.3              
     [73] Biostrings_2.62.0           pillar_1.7.0               
     [75] GenomicRanges_1.46.1        reshape2_1.4.4             
     [77] codetools_0.2-18            stats4_4.1.3               
     [79] glue_1.6.2                  ShortRead_1.52.0           
     [81] latticeExtra_0.6-29         data.table_1.14.2          
     [83] RcppParallel_5.1.5          png_0.1-7                  
     [85] vctrs_0.4.1                 foreach_1.5.2              
     [87] gtable_0.3.0                purrr_0.3.4                
     [89] tidyr_1.2.0                 morpheus_0.1.1.1           
     [91] cachem_1.0.6                ggplot2_3.3.6              
     [93] viridisLite_0.4.0           tibble_3.1.7               
     [95] iterators_1.0.14            GenomicAlignments_1.30.0   
     [97] memoise_2.0.1               IRanges_2.28.0             
     [99] cluster_2.1.3               ellipsis_0.3.2
    [11-01-2023 10:55:32 UTC] "allgraphs"(datafile="/nephele_data/outputs/OTU_table.txt", outdir="/nephele_data/outputs//graphs", mapfile="/nephele_data/outputs/N2_16S_example_mapping_file_min_corrected.txt.no_gz",tsvfile=TRUE, ...)
    [11-01-2023 10:55:32 UTC] Reading in map file /nephele_data/outputs/N2_16S_example_mapping_file_min_corrected.txt.no_gz
    [11-01-2023 10:55:32 UTC] Reading in OTU file /nephele_data/outputs/OTU_table.txt
    [11-01-2023 10:55:32 UTC] otu <- read.delim(datafile, check.names = FALSE, na.strings = '', row.names = 1)
    [11-01-2023 10:55:32 UTC] tax <- otu[,!names(otu) %in% map$SampleID]
    [11-01-2023 10:55:32 UTC] otu <- otu[, names(otu) %in% map$SampleID, drop=F]
    [11-01-2023 10:55:32 UTC] otu <- cbind(otu, tax)
    [11-01-2023 10:55:32 UTC] amp <- amp_load(otu, map)
    [11-01-2023 10:55:32 UTC] ampvis2 object with 3 elements.
    [11-01-2023 10:55:32 UTC] Summary of OTU table:
         Samples         OTUs  Total#Reads    Min#Reads    Max#Reads Median#Reads 
               2          214        24224        11885        12339        12112 
       Avg#Reads 
           12112
    [11-01-2023 10:55:32 UTC] Assigned taxonomy:
        Kingdom      Phylum       Class       Order      Family       Genus 
      214(100%) 212(99.07%)  211(98.6%) 210(98.13%) 193(90.19%) 140(65.42%) 
        Species 
          0(0%)
    [11-01-2023 10:55:33 UTC] Metadata variables: 7 
     SampleID, ForwardFastqFile, ReverseFastqFile, TreatmentGroup, Animal, Day, Description
    [11-01-2023 10:55:33 UTC] Rarefaction curve
    [11-01-2023 10:55:34 UTC] rarefactioncurve(outdir = outdir, amp = amp, colors = allcols)
    [11-01-2023 10:55:35 UTC] Saving plot to /nephele_data/outputs/graphs/rarecurve.html
    [11-01-2023 10:55:35 UTC] Saving rarefaction curve table to /nephele_data/outputs//graphs/rarecurve.txt
    [11-01-2023 10:55:35 UTC] Relative abundance heatmaps
    [11-01-2023 10:55:35 UTC] morphheatmap(outdir = outdir, amp = amp, colors=allcols, filter_level = 5)
    [11-01-2023 10:55:35 UTC] Filter taxa below 5 counts/abundance.
    [11-01-2023 10:55:35 UTC] amp <- filterlowabund(amp, level = 5, abs=T)
    [11-01-2023 10:55:35 UTC] Calculate relative abundance.
    [11-01-2023 10:55:35 UTC] amp <- subsetamp(amp, sampdepth = NULL, rarefy=FALSE, normalise = TRUE, printsummary = FALSE)
    [11-01-2023 10:55:35 UTC] makeheatmap("seq", amp)
    [11-01-2023 10:55:36 UTC] heatmap <- morpheus(mat, columns=columns, columnAnnotations = amptax$metadata, columnColorModel = list(type=as.list(colors)), colorScheme = list(scalingMode="fixed", values=values, colors=hmapcolors, stepped=FALSE), rowAnnotations = amptax$tax, rows = rows, dendrogram="none")
    [11-01-2023 10:55:37 UTC] Saving plot to /nephele_data/outputs/graphs/seq_heatmap.html
    [11-01-2023 10:55:37 UTC] Sampling depth: 10000
    [11-01-2023 10:55:37 UTC] Filter samples below 10000 counts.
    [11-01-2023 10:55:37 UTC] amp <- amp_subset_samples(amp, minreads = 10000, ...)
    [11-01-2023 10:55:37 UTC] ampvis2 object with 3 elements.
    [11-01-2023 10:55:37 UTC] Summary of OTU table:
         Samples         OTUs  Total#Reads    Min#Reads    Max#Reads Median#Reads 
               2          214        24224        11885        12339        12112 
       Avg#Reads 
           12112
    [11-01-2023 10:55:37 UTC] Assigned taxonomy:
        Kingdom      Phylum       Class       Order      Family       Genus 
      214(100%) 212(99.07%)  211(98.6%) 210(98.13%) 193(90.19%) 140(65.42%) 
        Species 
          0(0%)
    [11-01-2023 10:55:37 UTC] Metadata variables: 7 
     SampleID, ForwardFastqFile, ReverseFastqFile, TreatmentGroup, Animal, Day, Description
    [11-01-2023 10:55:37 UTC] Alpha diversity and PCoA plots will not be made, as they require at least 3 samples.  Only 2 remain after filtering.
    [11-01-2023 10:55:37 UTC] "allgraphs" complete.
    [11-01-2023 10:55:37 UTC] DADA2 pipeline complete.
    [11-01-2023 10:55:42 UTC] 0

