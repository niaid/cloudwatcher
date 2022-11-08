import datetime
import logging
from typing import Any, Dict, List, Optional

import boto3
import pytz

from cloudwatcher.cloudwatcher import CloudWatcher
from cloudwatcher.const import DEFAULT_QUERY_KWARGS
from cloudwatcher.metric_handlers import (
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
        dimensions_list: List[Dict[str, str]],
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

        Args:
            namespace (str): the namespace of the metric
            dimensions_list (List[Dict[str, str]]): the dimensions of the metric
            metric_name (str): the name of the metric
            metric_id (str): the ID of the metric
            metric_unit (Optional[str]): the unit of the metric
            aws_access_key_id (Optional[str]): the AWS access key ID
            aws_secret_access_key (Optional[str]): the AWS secret access key
            aws_session_token (Optional[str]): the AWS session token
            aws_region_name (Optional[str]): the AWS region name
        """
        super().__init__(
            service_name="cloudwatch",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            aws_region_name=aws_region_name,
        )
        self.namespace = namespace
        self.dimensions_list = dimensions_list
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

        Args:
            days (int): how many days to subtract from the current date to determine
                the metric collection start time
            hours (int): how many hours to subtract from the current time to determine
                the metric collection start time
            minutes (int): how many minutes to subtract from the current time to
                determine the metric collection start time
            stat (str): the statistic to query
            period (int): the period of the metric

        Returns:
            Dict: the response from the query, check the structure of the
            response [here](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.get_metric_data) # noqa: E501
        """
        # Create CloudWatch client
        now = datetime.datetime.now(pytz.utc)
        start_time = now - datetime.timedelta(days=days, hours=hours, minutes=minutes)

        _time = lambda x: x.strftime("%Y-%m-%d %H:%M:%S")

        _LOGGER.info(
            f"Querying '{self.metric_name}' for dimensions {self.dimensions_list} "
            f"from {_time(start_time)} to {_time(now)}"
        )

        response = self.client.get_metric_data(
            MetricDataQueries=[
                {
                    "Id": self.metric_id,
                    "MetricStat": {
                        "Metric": {
                            "Namespace": self.namespace,
                            "MetricName": self.metric_name,
                            "Dimensions": [dim.dict() for dim in self.dimensions_list],
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

        Args:
            ec2_instance_id (str): the ID of the EC2 instance
            days (int): how many days to subtract from the current date to determine
                the metric collection start time
            hours (int): how many hours to subtract from the current time to determine
                 the metric collection start time
            minutes (int): how many minutes to subtract from the current time to
                determine the metric collection start time

        Returns:
            int: the runtime of the EC2 instance in minutes
        """
        if not self.is_ec2_running(ec2_instance_id):
            _LOGGER.info(
                f"Instance '{self.dimension_value}' is not running anymore. "
                f"Uptime will be estimated based on reported metrics in "
                f"the last {days} days"
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
                period=60,  # most precise period that AWS stores for instances where
                # start time is between 3 hours and 15 days ago
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

        Args:
            ec2_instance_id (str): the ID of the EC2 instance

        Returns:
            bool: True if EC2 instance is running, False otherwise
        """
        instances = self.ec2_resource.instances.filter(
            Filters=[{"Name": "instance-id", "Values": [ec2_instance_id]}]
        )
        if len(list(instances)) == 0:
            return None
        if len(list(instances)) > 1:
            raise Exception(f"Multiple EC2 instances matched by ID: {ec2_instance_id}")
        for instance in instances:
            # check the status codes and their meanings:
            # https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_InstanceState.html # noqa: E501
            if instance.state["Code"] <= 16:
                return True
        return False

    @staticmethod
    def timed_metric_factory(response: dict) -> List[TimedMetric]:
        """
        Create a collection of TimedMetrics from the CloudWatch client response.

        Args:
            response (dict): the response from the query

        Returns:
            List[TimedMetric]: a collection of TimedMetrics
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
        **kwargs,
    ) -> None:
        """
        Internal method to execute a TimedMetricHandler

        Args:
            handler_class (TimedMetricHandler): the TimedMetricHandler to execute
            response (Optional[Dict]): the response from the query
            query_kwargs (Optional[Dict]): the query kwargs to use for the query
            **kwargs: additional kwargs to pass to the handler
        """
        _LOGGER.debug(f"Executing '{handler_class.__name__}'")
        response = response or self.query_ec2_metrics(**query_kwargs)
        timed_metrics = self.timed_metric_factory(response)
        for timed_metric in timed_metrics:
            if len(timed_metric.values) < 1:
                continue
            handler = handler_class(timed_metric=timed_metric)
            handler(**kwargs)

    def _exec_response_handler(
        self,
        handler_class: ResponseHandler,
        response: Optional[Dict] = None,
        query_kwargs: Optional[Dict] = None,
        **kwargs,
    ) -> None:
        """
        Internal method to execute a ResponseHandler

        Args:
            handler_class (ResponseHandler): the ResponseHandler to execute
            response (Optional[Dict]): the response from the query
            query_kwargs (Optional[Dict]): the query kwargs to use for the query
            **kwargs: additional kwargs to pass to the handler

        """
        _LOGGER.debug(f"Executing '{handler_class.__name__}'")
        response = response or self.query_ec2_metrics(**query_kwargs)
        handler = handler_class(response=response)
        handler(**kwargs)

    def save_metric_json(
        self,
        file_path: str,
        response: Optional[Dict] = None,
        query_kwargs: Optional[Dict] = None,
    ):
        """
        Query and save the metric data to a JSON file

        Args:
            file_path (str): the file path to save the metric data to
            response (Optional[Dict]): the response from the query
            query_preset (Optional[str]): the query preset to use for the query
        """
        self._exec_timed_metric_handler(
            TimedMetricJsonSaver,
            target=file_path,
            response=response,
            query_kwargs=query_kwargs,
        )

    def save_metric_csv(
        self,
        file_path: str,
        response: Optional[Dict] = None,
        query_kwargs: Optional[Dict] = None,
    ):
        """
        Query and save the metric data to a CSV file

        Args:
            file_path (str): the file path to save the metric data to
            response (Optional[Dict]): the response from the query
            query_preset (Optional[str]): the query preset to use for the query
        """
        self._exec_timed_metric_handler(
            TimedMetricCsvSaver,
            target=file_path,
            response=response,
            query_kwargs=query_kwargs,
        )

    def log_metric(
        self, response: Optional[Dict] = None, query_preset: Optional[str] = None
    ):
        """
        Query and log the metric data

        Args:
            response (Optional[Dict]): the response from the query
            query_preset (Optional[str]): the query preset to use for the query
        """
        self._exec_timed_metric_handler(
            TimedMetricLogger,
            target=None,  # TODO: add support for saving to file
            response=response,
        )

    def save_metric_plot(
        self,
        file_path: str,
        response: Optional[Dict] = None,
        query_kwargs: Optional[Dict] = None,
    ):
        """
        Query and plot the metric data

        Args:
            file_path (str): the file path to save the metric data to
            response (Optional[Dict]): the response from the query
            query_preset (Optional[str]): the query preset to use for the query
        """
        self._exec_timed_metric_handler(
            TimedMetricPlotter,
            target=file_path,
            metric_unit=self.metric_unit,
            response=response,
            query_kwargs=query_kwargs,
        )

    def log_metric_summary(self, response: Optional[Dict] = None):
        """
        Query and summarize the metric data to a JSON file

        Args:
            response (Optional[Dict]): the response from the query
            query_preset (Optional[str]): the query preset to use for the query
        """
        self._exec_timed_metric_handler(
            TimedMetricSummarizer,
            target=None,  # TODO: add support for saving to file
            metric_unit=self.metric_unit,
            summarizer=("Max", max),
            response=response,
        )

    def save_response_json(
        self,
        file_path: str,
        response: Optional[Dict] = None,
        query_kwargs: Optional[Dict] = None,
    ):
        """
        Query and save the response data to a JSON file

        Args:
            file_path (str): the file path to save the response data to
            response (Optional[Dict]): the response from the query
            query_preset (Optional[str]): the query preset to use for the query
        """
        self._exec_response_handler(
            ResponseSaver,
            target=file_path,
            response=response,
            query_kwargs=query_kwargs,
        )

    def log_response(self, response: Optional[Dict] = None):
        """
        Query and log the response

        Args:
            response (Optional[Dict]): the response from the query
            query_preset (Optional[str]): the query preset to use for the query
        """
        self._exec_response_handler(
            ResponseLogger,
            target=None,
            response=response,
        )
