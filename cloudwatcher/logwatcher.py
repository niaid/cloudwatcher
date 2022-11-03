# TODO: query the AWS multiple times if query json provided

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from cloudwatcher.cloudwatcher import CloudWatcher

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

        Args:
            log_group_name (str): The name of the log group
            log_stream_name (str): The name of the log stream
            start_token (Optional[str]): The token to use for the next query. Defaults to None
            aws_access_key_id (Optional[str]): The AWS access key ID. Defaults to None
            aws_secret_access_key (Optional[str]): The AWS secret access key. Defaults to None
            aws_session_token (Optional[str]): The AWS session token. Defaults to None
            aws_region_name (Optional[str]): The AWS region name. Defaults to 'us-east-1'
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

        Returns:
            str: The string representation of the object
        """
        return f"LogWatcher('{self.log_group_name}/{self.log_stream_name}')"

    def check_log_exists(self) -> bool:
        """
        Check if the log stream exists

        Returns:
            bool: True if the log stream exists, False otherwise
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

        Args:
            query_kwargs (Dict[str, Any]): The query arguments
        Returns:
            List[Event]: The list of log events
        """
        response = self.client.get_log_events(**query_kwargs)
        query_kwargs.update({"nextToken": response["nextForwardToken"]})
        return response["events"], response["nextForwardToken"]

    def stream_cloudwatch_logs(
        self, events_limit: int = 1000, max_retry_attempts: int = 5
    ) -> List[Event]:
        """
        A generator that retrieves desired number of log events per iteration

        Args:
            events_limit (int): The number of events to retrieve per iteration.
            max_retry_attempts (int): The number of retry attempts.
        Returns:
            List[Event]: The list of log events
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

        Args:
            events_limit (int): The number of events to retrieve per iteration.
            max_retry_attempts (int): The number of retry attempts.
            sep (str): The separator to use between log events.
        Returns:
            Tuple[List[str], str]: The list of formatted log events and the next token
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

        Args:
            events_limit (int): The number of events to retrieve per iteration.
            max_retry_attempts (int): The number of retry attempts.
        Returns:
            Tuple[str, str]: The list of formatted log events and the next token
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

        Args:
            log_events (List[Event]): The list of log events.
            regex (str): The regex to use to extract the time and message.
            fmt_str (str): The format string to use to format the time and message.
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

        Args:
            file_path (str): The path to save the log file to.
        """
        logs, _ = self.return_formatted_logs()
        with open(file_path, "w") as f:
            f.write(logs)
        _LOGGER.info(
            f"Logs '{self.log_group_name}/{self.log_stream_name}' saved to: {file_path}"
        )
