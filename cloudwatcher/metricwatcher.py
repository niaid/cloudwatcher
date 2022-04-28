import datetime
import logging
from typing import Any, Dict, List, Optional

import boto3
import pytz

from .cloudwatcher import CloudWatcher
from .const import DEFAULT_QUERY_KWARGS, QUERY_KWARGS_PRESETS
from .metric_handlers import (
    ResponseHandler,
    ResponseLogger,
    ResponseSaver,
    TimedMetric,
    TimedMetricCsvSaver,
    TimedMetricHandler,
    TimedMetricJsonSaver,
    TimedMetricLogger,
    TimedMetricPlotter,
    TimedMetricSummarizer,
)

_LOGGER = logging.getLogger(__name__)


class MetricWatcher(CloudWatcher):
    """
    A class for AWS CloudWatch metric retrieval and parsing
    """

    def __init__(
        self,
        namespace: str,
        dimension_name: str,
        dimension_value: str,
        metric_name: str,
        metric_id: str,
        metric_unit: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        aws_region_name: Optional[str] = None,
    ) -> None:
        """
        Initialize MetricWatcher

        :param str namespace: The namespace of the metric
        :param Optional[str] region_name: The name of the region. Defaults to 'us-east-1'
        :param Optional[str] start_token: The start token to use for the query
        """
        super().__init__(
            service_name="cloudwatch",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            aws_region_name=aws_region_name,
        )
        self.namespace = namespace
        self.dimension_name = dimension_name
        self.dimension_value = dimension_value
        self.metric_name = metric_name
        self.metric_id = metric_id
        self.metric_unit = metric_unit
        self.ec2_resource = boto3.resource(
            service_name="ec2",
            region_name=self.aws_region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
        )

    def query_ec2_metrics(
        self,
        days: int,
        hours: int,
        minutes: int,
        stat: str,
        period: int,
    ) -> Dict:
        """
        Query EC2 metrics

        :param str namespace: namespace to monitor the metrics within. This value must match the 'Nampespace' value in the config
        :param int days: how many days to subtract from the current date to determine the metric collection start time
        :param int hours: how many hours to subtract from the current time to determine the metric collection start time
        :param int minute: how many minutes to subtract from the current time to determine the metric collection start time
        :param str stat: stat to use, e.g. 'Maximum'
        :param int period: the granularity, in seconds, of the returned data points
        return dict: metric statistics response, check the structure of the response [here](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.get_metric_data)
        """
        # Create CloudWatch client
        now = datetime.datetime.now(pytz.utc)
        start_time = now - datetime.timedelta(days=days, hours=hours, minutes=minutes)

        _LOGGER.info(
            f"Querying '{self.metric_name}' for dimension "
            f"('{self.dimension_name}'='{self.dimension_value}') from "
            f"{start_time.strftime('%H:%M:%S')} to {now.strftime('%H:%M:%S')}"
        )

        response = self.client.get_metric_data(
            MetricDataQueries=[
                {
                    "Id": self.metric_id,
                    "MetricStat": {
                        "Metric": {
                            "Namespace": self.namespace,
                            "MetricName": self.metric_name,
                            "Dimensions": [
                                {
                                    "Name": self.dimension_name,
                                    "Value": self.dimension_value,
                                }
                            ],
                        },
                        "Stat": stat,
                        "Unit": str(
                            self.metric_unit
                        ),  # str(None) is desired, if no unit is specified
                        "Period": period,
                    },
                },
            ],
            StartTime=start_time,
            EndTime=now,
        )
        resp_status = response["ResponseMetadata"]["HTTPStatusCode"]
        if resp_status != 200:
            _LOGGER.error(f"Invalid response status code: {resp_status}")
            return
        _LOGGER.debug(f"Response status code: {resp_status}")
        return response

    def get_ec2_uptime(
        self,
        ec2_instance_id: str,
        days: int,
        hours: int,
        minutes: int,
    ) -> int:
        """
        Get the runtime of an EC2 instance

        :param int days: how many days to subtract from the current date to determine the metric collection start time
        :param int hours: how many hours to subtract from the current time to determine the metric collection start time
        :param int minute: how many minutes to subtract from the current time to determine the metric collection start time
        :param str ec2_instance_id: the ID of the EC2 instance to query
        Returns:
            int: runtime of the instance in seconds
        """
        if not self.is_ec2_running(ec2_instance_id):
            _LOGGER.info(
                f"Instance '{self.dimension_value}' is not running anymore. "
                f"Uptime will be estimated based on reported metrics in the last {days} days"
            )
            instances = self.ec2_resource.instances.filter(
                Filters=[{"Name": "instance-id", "Values": [self.dimension_value]}]
            )
            # get the latest reported metric
            metrics_response = self.query_ec2_metrics(
                days=days,
                hours=hours,
                minutes=minutes,
                stat="Maximum",  # any stat works
                period=60,  # most precise period that AWS stores for instances where start time is between 3 hours and 15 days ago
            )
            # extract the latest metric report time
            timed_metrics = self.timed_metric_factory(metrics_response)
            try:
                earliest_metric_report_time = timed_metrics[-1].timestamps[0]
                latest_metric_report_time = timed_metrics[-1].timestamps[-1]
                return (
                    earliest_metric_report_time - latest_metric_report_time
                ).total_seconds()
            except IndexError:
                _LOGGER.warning(f"No metric data found for EC2: {self.dimension_value}")
                return
        instances = self.ec2_resource.instances.filter(
            Filters=[{"Name": "instance-id", "Values": [self.dimension_value]}]
        )
        for instance in instances:
            _LOGGER.info(
                f"Instance '{self.dimension_value}' is still running. "
                f"Launch time: {instance.launch_time}"
            )
            return (datetime.now(pytz.utc) - instance.launch_time).total_seconds()

    def is_ec2_running(self, ec2_instance_id: str) -> bool:
        """
        Check if EC2 instance is running

        :param str ec2_instance_id: the ID of the EC2 instance to query
        :returns bool: True if instance is running, False otherwise
        """
        instances = self.ec2_resource.instances.filter(
            Filters=[{"Name": "instance-id", "Values": [ec2_instance_id]}]
        )
        if len(list(instances)) == 0:
            return None
        if len(list(instances)) > 1:
            raise Exception(f"Multiple EC2 instances matched by ID: {ec2_instance_id}")
        for instance in instances:
            # check the status codes and their meanings: https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_InstanceState.html
            if instance.state["Code"] <= 16:
                return True
        return False

    @staticmethod
    def timed_metric_factory(response: dict) -> List[TimedMetric]:
        """
        Create a collection of TimedMetrics from the CloudWatch client response.

        :param dict response: response from CloudWatch client
        :return List[TimedMetric]: list of TimedMetric objects
        """
        return [
            TimedMetric(
                label=metric_data_result["Label"],
                timestamps=metric_data_result["Timestamps"],
                values=metric_data_result["Values"],
            )
            for metric_data_result in response["MetricDataResults"]
        ]

    def _exec_timed_metric_handler(
        self,
        handler_class: TimedMetricHandler,
        response: Optional[Dict] = None,
        query_kwargs: Optional[Dict] = None,
        query_preset: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Internal method to execute a TimedMetricHandler

        :param TimedMetricHandler handler_class: TimedMetricHandler class to execute
        :param dict response: response from CloudWatch client
        :param dict query_kwargs: kwargs to pass to the EC2 query
        :param str query_preset: period preset to use for the EC2 query
        :param kwargs: keyword arguments to pass to the handler
        """
        _LOGGER.debug(f"Executing '{handler_class.__name__}'")
        query_kwargs = query_kwargs or self._get_query_kwargs(query_preset)
        response = response or self.query_ec2_metrics(**query_kwargs)
        timed_metrics = self.timed_metric_factory(response)
        for timed_metric in timed_metrics:
            if len(timed_metric.values) < 1:
                continue
            handler = handler_class(timed_metric=timed_metric)
            handler(**kwargs)

    def _get_query_kwargs(self, preset_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Based on the selected preset identifier get the query values

        :param str preset_key: preset identifier:param dict query_kwargs: kwargs to pass to the EC2 query
        :param dict query_kwargs: kwargs to pass to the EC2 query
        :param str query_preset: period preset to use for the EC2 query
        :return Dict[str, Any]: query values
        """
        if preset_key is None:
            return DEFAULT_QUERY_KWARGS
        if preset_key not in QUERY_KWARGS_PRESETS:
            raise KeyError(
                f"Invalid preset key: {preset_key}."
                f"Valid keys are: {list(QUERY_KWARGS_PRESETS.keys())}"
            )
        return QUERY_KWARGS_PRESETS.get(preset_key)

    def _exec_response_handler(
        self,
        handler_class: ResponseHandler,
        response: Optional[Dict] = None,
        query_kwargs: Optional[Dict] = None,
        query_preset: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Internal method to execute a ResponseHandler

        :param ResponseHandler handler_class: ResponseHandler class to execute
        :param dict response: response from `query_ec2_metrics` method
        :param dict query_kwargs: kwargs to pass to the EC2 query
        :param str query_preset: period preset to use for the EC2 query
        """
        _LOGGER.debug(f"Executing '{handler_class.__name__}'")
        query_kwargs = query_kwargs or self._get_query_kwargs(query_preset)
        response = response or self.query_ec2_metrics(**query_kwargs)
        handler = handler_class(response=response)
        handler(**kwargs)

    def save_metric_json(
        self,
        file_path: str,
        response: Optional[Dict] = None,
        query_preset: Optional[str] = None,
    ):
        """
        Query and save the metric data to a JSON file

        :param str file_path: path to the file to save the metric data to
        :param dict response: response retrieved with `query_ec2_metrics`.
             A query is performed if not provided.
        :param dict response: response from `query_ec2_metrics` method
        :param dict query_kwargs: kwargs to pass to the EC2 query
        :param str query_preset: period preset to use for the EC2 query
        """
        self._exec_timed_metric_handler(
            TimedMetricJsonSaver,
            target=file_path,
            response=response,
            query_preset=query_preset,
        )

    def save_metric_csv(
        self,
        file_path: str,
        response: Optional[Dict] = None,
        query_preset: Optional[str] = None,
    ):
        """
        Query and save the metric data to a CSV file

        :param str file_path: path to the file to save the metric data to
        :param dict response: response retrieved with `query_ec2_metrics`.
             A query is performed if not provided.
        :param dict response: response from `query_ec2_metrics` method
        :param dict query_kwargs: kwargs to pass to the EC2 query
        :param str query_preset: period preset to use for the EC2 query
        """
        self._exec_timed_metric_handler(
            TimedMetricCsvSaver,
            target=file_path,
            response=response,
            query_preset=query_preset,
        )

    def log_metric(
        self, response: Optional[Dict] = None, query_preset: Optional[str] = None
    ):
        """
        Query and log the metric data

        :param kwargs: keyword arguments to pass to the handler
        :param dict response: response retrieved with `query_ec2_metrics`.
             A query is performed if not provided.
        :param dict response: response from `query_ec2_metrics` method
        :param dict query_kwargs: kwargs to pass to the EC2 query
        :param str query_preset: period preset to use for the EC2 query
        """
        self._exec_timed_metric_handler(
            TimedMetricLogger,
            target=None,  # TODO: add support for saving to file
            response=response,
            query_preset=query_preset,
        )

    def save_metric_plot(
        self,
        file_path: str,
        response: Optional[Dict] = None,
        query_preset: Optional[str] = None,
    ):
        """
        Query and plot the metric data

        :param str file_path: path to the file to plot the metric data to
        :param kwargs: keyword arguments to pass to the plotter
        :param dict response: response retrieved with `query_ec2_metrics`.
             A query is performed if not provided.
        :param dict response: response from `query_ec2_metrics` method
        :param dict query_kwargs: kwargs to pass to the EC2 query
        :param str query_preset: period preset to use for the EC2 query
        """
        self._exec_timed_metric_handler(
            TimedMetricPlotter,
            target=file_path,
            metric_unit=self.metric_unit,
            response=response,
            query_preset=query_preset,
        )

    def log_metric_summary(
        self, response: Optional[Dict] = None, query_preset: Optional[str] = None
    ):
        """
        Query and summarize the metric data to a JSON file

        :param str file_path: path to the file to save the metric data to
        :param dict response: response retrieved with `query_ec2_metrics`.
             A query is performed if not provided.
        :param dict response: response from `query_ec2_metrics` method
        :param dict query_kwargs: kwargs to pass to the EC2 query
        :param str query_preset: period preset to use for the EC2 query
        """
        self._exec_timed_metric_handler(
            TimedMetricSummarizer,
            target=None,  # TODO: add support for saving to file
            metric_unit=self.metric_unit,
            summarizer=("Max", max),
            response=response,
            query_preset=query_preset,
        )

    def save_response_json(
        self,
        file_path: str,
        response: Optional[Dict] = None,
        query_preset: Optional[str] = None,
    ):
        """
        Query and save the response data to a JSON file

        :param str file_path: path to the file to save the response data to
        :param dict response: response retrieved with `query_ec2_metrics`.
             A query is performed if not provided.
        :param dict response: response from `query_ec2_metrics` method
        :param dict query_kwargs: kwargs to pass to the EC2 query
        :param str query_preset: period preset to use for the EC2 query
        """
        self._exec_response_handler(
            ResponseSaver,
            target=file_path,
            response=response,
            query_preset=query_preset,
        )

    def log_response(
        self, response: Optional[Dict] = None, query_preset: Optional[str] = None
    ):
        """
        Query and log the response

        :param dict response: response retrieved with `query_ec2_metrics`.
             A query is performed if not provided.
        :param dict response: response from `query_ec2_metrics` method
        :param dict query_kwargs: kwargs to pass to the EC2 query
        :param str query_preset: period preset to use for the EC2 query
        """
        self._exec_response_handler(
            ResponseLogger,
            target=None,
            response=response,
            query_preset=query_preset,
        )
