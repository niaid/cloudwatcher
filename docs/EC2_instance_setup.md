# EC2 instance setup

!!! info "Using ECS ContainerInsights?"

    **This section may not be required for your setup**. For instance, if you plan to monitor ECS containers that report the metrics with [ECS ContainerInsights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/deploy-container-insights-ECS-cluster.html).

In order to use the tool a `CloudWatchAgent` process must be running on the EC2 instance to be monitored.

Please refer to [this page](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/install-CloudWatch-Agent-commandline-fleet.html) to learn how to install and start the `CloudWatchAgent` on an EC2 instance.

## Configuration

`CloudWatchAgent` is a powerful tool and can be [configured](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Agent-Configuration-File-Details.html) to report variety of metrics.

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

### EC2 userdata

The tool can be configured to be launched automatically by the EC2 instance userdata. Here are the steps to configure the tool to be launched automatically:

1. Download `CloudWatchAgent` appropriate for your EC2 instance type; learn more [here](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/download-cloudwatch-agent-commandline.html).
2. Install `CloudWatchAgent` on the EC2 instance.
3. Create/copy a `CloudWatchAgent` configuration file.
4. Start the `CloudWatchAgent` service pointing to the created configuration file.

For a Debian EC2 instance, the steps can be achieved by executing the following commands:

```bash linenums="1" title="ec2_userdata.sh"
#!/bin/bash
CLOUDWATCH_CFG_SRC=<path-in-repo>/config.json
CLOUDWATCH_CFG_FILE=/opt/aws/amazon-cloudwatch-agent/bin/config.json

wget https://s3.amazonaws.com/amazoncloudwatch-agent/debian/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i -E ./amazon-cloudwatch-agent.deb
cp $CLOUDWATCH_CFG_SRC $CLOUDWATCH_CFG_FILE
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:$CLOUDWATCH_CFG_FILE
```
