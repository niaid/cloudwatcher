# EC2 instance setup

In order to use the tool a `CloudWatchAgent` process must be running on the EC2 instance to be monitored.

Please refer to [this page](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/install-CloudWatch-Agent-commandline-fleet.html) to learn how to install and start the `CloudWatchAgent` on an EC2 instance.

## Configuration

`CloudWatchAgent` is a powerful tool and can be [configured](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Agent-Configuration-File-Details.html) to report variety of metrics. The configuration file is located at `/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json` in each EC2 instance and is sourced from a file in the nephele2 repository: `resources/misc_files_for_worker/cloudwatch_agent_cfg.json`.

Here is an example of the configuration file:

```json linenums="1" title="cloudwatch_agent_cfg.json"
{
  "agent": {
    "metrics_collection_interval": 10
  },
  "metrics": {
    "namespace": "ExampleNamespace",
    "metrics_collected": {
      "mem": {
        "measurement": ["mem_used", "mem_cached", "mem_total"],
        "metrics_collection_interval": 1
      }
    },
    "append_dimensions": {
      "InstanceId": "${aws:InstanceId}"
    }
  }
}
```

The above configuration file is used to colect 3 memory metrics every second:

- `mem_used`
- `mem_cached`
- `mem_total`
