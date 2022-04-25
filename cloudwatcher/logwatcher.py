# TODO: query the AWS multiple times if query json provided

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .cloudwatcher import CloudWatcher

Event = Dict[str, str]

_LOGGER = logging.getLogger(__name__)


class LogWatcher(CloudWatcher):
    """
    A class for AWS CloudWatch log events retrieval and parsing
    """

    def __init__(
        self,
        log_group_name: str,
        log_stream_name: str,
        start_token: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        aws_region_name: Optional[str] = None,
    ) -> None:
        """
        Initialize LogWatcher

        :param str log_group_name: The name of the log group
        :param str log_stream_name: The name of the log stream
        :param Optional[str] region_name: The name of the region. Defaults to 'us-east-1'
        :param Optional[str] start_token: The start token to use for the query
        """
        super().__init__(
            service_name="logs",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            aws_region_name=aws_region_name,
        )
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name
        self.start_token = start_token

    def __repr__(self) -> str:
        """
        Return a string representation of the object

        :return: A string representation of the object
        """
        return f"LogWatcher('{self.log_group_name}/{self.log_stream_name}')"

    def check_log_exists(self) -> bool:
        """
        Check if the log stream exists

        :return bool: True if the log stream exists, False otherwise
        """
        try:
            response = self.client.describe_log_streams(
                logGroupName=self.log_group_name,
                logStreamNamePrefix=self.log_stream_name,
            )
            return True if response["logStreams"] else False
        except Exception as e:
            _LOGGER.error(f"Error checking if log stream exists: {e}")
            return False

    def _get_events(self, query_kwargs: Dict[str, Any]) -> List[Event]:
        """
        Get events from CloudWatch and update the arguments
        for the next query with 'nextForwardToken'

        :param Dict[str, Any] query_kwargs: The query arguments
        :return List[Event]: The list of events
        """
        response = self.client.get_log_events(**query_kwargs)
        query_kwargs.update({"nextToken": response["nextForwardToken"]})
        return response["events"], response["nextForwardToken"]

    def stream_cloudwatch_logs(
        self, events_limit: int = 1000, max_retry_attempts: int = 5
    ) -> List[Event]:
        """
        A generator that retrieves desired number of log events per iteration

        :param str log_group_name: The name of the log group
        :param str log_stream_name: The name of the log stream
        :param int events_limit: The number of events to retrieve per iteration
        :return List[Event]: The list of log events
        """
        query_kwargs = dict(
            logGroupName=self.log_group_name,
            logStreamName=self.log_stream_name,
            limit=events_limit,
            startFromHead=True,
        )
        if self.start_token:
            query_kwargs.update({"nextToken": self.start_token})
        _LOGGER.debug(
            f"Retrieving log events from: {self.log_group_name}/{self.log_stream_name}"
        )
        events, token = self._get_events(query_kwargs)
        yield events, token
        while events:
            events, token = self._get_events(query_kwargs)
            retry_attempts = 0
            while not events and max_retry_attempts > retry_attempts:
                events, token = self._get_events(query_kwargs)
                retry_attempts += 1
                _LOGGER.debug(
                    f"Received empty log events list. Retry attempt: {retry_attempts}"
                )
            yield events, token

    def stream_formatted_logs(
        self,
        events_limit: int = 1000,
        max_retry_attempts: int = 5,
        sep: str = "<br>",
    ) -> Tuple[List[str], str]:
        """
        A generator that yields formatted log events

        :param Optional[int] events_limit: The number of events to retrieve per iteration. Defaults to 1000
        :param Optional[int] max_retry_attempts: The number of retry attempts. Defaults to 5
        :param Optional[str] sep: The format string to use for formatting the log event. Defaults to "<br>"
        :return Tuple[List[str], str]: The list of formatted log events and the token to use for the next query
        """
        for events, token in self.stream_cloudwatch_logs(
            events_limit=events_limit,
            max_retry_attempts=max_retry_attempts,
        ):
            yield sep.join(self.format_logs_events(log_events=events)), token

    def return_formatted_logs(
        self, events_limit: int = 1000, max_retry_attempts: int = 5
    ) -> Tuple[str, str]:
        """
        A generator that yields formatted log events

        :param Optional[int] events_limit: The number of events to retrieve per iteration. Defaults to 1000
        :param Optional[int] max_retry_attempts: The number of retry attempts. Defaults to 5
        :return Tuple[List[str], str]: formatted log events and the token to use for the next query
        """
        formatted_events = ""
        for events, token in self.stream_cloudwatch_logs(
            events_limit=events_limit, max_retry_attempts=max_retry_attempts
        ):
            formatted_events += "\n".join(self.format_logs_events(log_events=events))
        return formatted_events, token

    def format_logs_events(
        self,
        log_events: List[Event],
        regex: str = r"^\[\d+-\d+-\d+\s\d+:\d+:\d+(.|,)\d+(\]|\s-\s\w+\])",
        fmt_str: str = "[{time} UTC] {message}",
    ) -> List[str]:
        """
        Format log events

        :param List[Event] log_events: The list of log events
        :param str regex: The regex to use for extracting the timestamp
        :param str fmt_str: The format string to use for formatting the log event
        :return List[str]: The list of formatted log events
        """

        def _datestr(timestamp: int, fmt_str: str = "%d-%m-%Y %H:%M:%S") -> str:
            """
            Convert milliseconds after Jan 1, 1970 UTC to a string date repr
            Args:
                timestamp (int): milliseconds after Jan 1, 1970 UTC
                fmt_str (str): format string for the date
            Returns:
                str: date string
            """
            return datetime.fromtimestamp(timestamp / 1000.0).strftime(fmt_str)

        formatted_log_list = []
        for e in log_events:
            m = re.search(regex, e["message"])
            msg = e["message"][m.end() :] if m else e["message"]
            formatted_log_list.append(
                fmt_str.format(time=_datestr(e["timestamp"]), message=msg.strip())
            )
        return formatted_log_list

    def save_log_file(self, file_path: str) -> None:
        """
        Save the log file to the specified path

        :param str log_file_path: The path to save the log file
        """
        logs, _ = self.return_formatted_logs()
        with open(file_path, "w") as f:
            f.write(logs)
        _LOGGER.info(
            f"Logs '{self.log_group_name}/{self.log_stream_name}' saved to: {file_path}"
        )
