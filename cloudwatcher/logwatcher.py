import logging
import re
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional, Tuple

from pydantic import BaseModel

from cloudwatcher.cloudwatcher import CloudWatcher

_LOGGER = logging.getLogger(__name__)


class LogEvent(BaseModel):
    """
    A class for AWS CloudWatch log events

    Attributes:
        message (str): The log message
        timestamp (datetime): The log timestamp
    """

    message: str
    timestamp: datetime

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> "LogEvent":
        """
        Create a LogEvent object from a response

        Args:
            response (Dict[str, Any]): The response from AWS

        Returns:
            LogEvent: The LogEvent object
        """
        return cls(
            message=response["message"],
            timestamp=datetime.fromtimestamp(response["timestamp"] / 1000),
        )

    def format_message(
        self,
        regex: Optional[str] = None,
        fmt_str_log: Optional[str] = None,
        fmt_str_datetime: Optional[str] = None,
    ) -> "LogEvent":
        """
        Format the message by removing the embedded timestamp and adding a UTC timestamp

        Args:
            regex (str): regex to match the timestamp in the message
            fmt_str_log (str): format string for the log message
            fmt_str_datetime (str): format string for the datetime

        Returns:
            str: formatted message
        """
        regex = regex or r"^\[\d+-\d+-\d+\s\d+:\d+:\d+(.|,)\d+(\]|\s-\s\w+\])"
        fmt_str_log = fmt_str_log or "[{time} UTC] {message}"
        fmt_str_datetime = fmt_str_datetime or "%d-%m-%Y %H:%M:%S"
        m = re.search(regex, self.message)
        msg = self.message[m.end() :] if m else self.message
        formatted_message = fmt_str_log.format(
            time=self.timestamp.strftime(fmt_str_datetime), message=msg.strip()
        )
        return LogEvent(message=formatted_message, timestamp=self.timestamp)

    def __bool__(self) -> bool:
        """
        Return True if the message is not empty

        Returns:
            bool: True if the message is not empty
        """
        return bool(self.message)


class LogEventsList(BaseModel):
    """
    A class for AWS CloudWatch log events list

    Attributes:
        events (List[LogEvent]): The list of log events
        next_forward_token (Optional[str]): The next forward token
        next_backward_token (Optional[str]): The next backward token
    """

    events: List[LogEvent]
    next_forward_token: Optional[str]
    next_backward_token: Optional[str]

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> "LogEventsList":
        """
        Create a LogEventsList object from a response

        Args:
            response (Dict[str, Any]): The response from AWS

        Returns:
            LogEventsList: The LogEventsList object
        """
        return cls(
            events=[LogEvent.from_response(event) for event in response["events"]],
            next_forward_token=response.get("nextForwardToken"),
            next_backward_token=response.get("nextBackwardToken"),
        )

    def format_messages(
        self,
        regex: Optional[str] = None,
        fmt_str_datetime: Optional[str] = None,
        fmt_str_log: Optional[str] = None,
    ) -> "LogEventsList":
        """
        Format the messages by removing the embedded timestamp
        and adding a UTC timestamp

        Args:
            regex (str): regex to match the timestamp in the message
            fmt_str_log (str): format string for the log message
            fmt_str_datetime (str): format string for the datetime

        Returns:
            LogEventsList: The LogEventsList object, with formatted messages
        """
        self.events = [
            event.format_message(
                regex=regex, fmt_str_datetime=fmt_str_datetime, fmt_str_log=fmt_str_log
            )
            for event in self.events
        ]
        return self

    def __bool__(self) -> bool:
        """
        Return True if the events list is not empty

        Returns:
            bool: True if the events list is not empty
        """
        return bool(self.events)


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
            start_token (Optional[str]): The token to use for the next query
            aws_access_key_id (Optional[str]): The AWS access key ID
            aws_secret_access_key (Optional[str]): The AWS secret access key
            aws_session_token (Optional[str]): The AWS session token
            aws_region_name (Optional[str]): The AWS region name
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

    def _get_events(self, query_kwargs: Dict[str, Any]) -> LogEventsList:
        """
        Get events from CloudWatch and update the arguments
        for the next query with 'nextForwardToken'

        Args:
            query_kwargs (Dict[str, Any]): The query arguments
        Returns:
            List[Event]: The list of log events
        """
        response = self.client.get_log_events(**query_kwargs)
        log_events_list = LogEventsList.from_response(response)
        query_kwargs.update({"nextToken": log_events_list.next_forward_token})
        return log_events_list

    def stream_cloudwatch_logs(
        self, events_limit: int = 1000, max_retry_attempts: int = 5
    ) -> Generator[LogEventsList, None, None]:
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
        log_events_list = self._get_events(query_kwargs)
        yield log_events_list
        while log_events_list:
            log_events_list = self._get_events(query_kwargs)
            retry_attempts = 0
            while not log_events_list and max_retry_attempts > retry_attempts:
                log_events_list = self._get_events(query_kwargs)
                retry_attempts += 1
                _LOGGER.debug(
                    f"Received empty log events list. Retry attempt: {retry_attempts}"
                )
            yield log_events_list

    def stream_formatted_logs(
        self,
        events_limit: int = 1000,
        max_retry_attempts: int = 5,
        sep: str = "<br>",
    ) -> Generator[Tuple[str, Optional[str]], None, None]:
        """
        A generator that yields formatted log events

        Args:
            events_limit (int): The number of events to retrieve per iteration.
            max_retry_attempts (int): The number of retry attempts.
            sep (str): The separator to use between log events.
        Returns:
            Tuple[List[str], str]: The list of formatted log events and the next token
        """
        for log_events_list in self.stream_cloudwatch_logs(
            events_limit=events_limit,
            max_retry_attempts=max_retry_attempts,
        ):
            formatted_log_events = log_events_list.format_messages().events
            yield sep.join(
                [event.message for event in formatted_log_events]
            ), log_events_list.next_forward_token

    def return_formatted_logs(
        self, events_limit: int = 1000, max_retry_attempts: int = 5
    ) -> Tuple[str, Optional[str]]:
        """
        A generator that yields formatted log events

        Args:
            events_limit (int): The number of events to retrieve per iteration.
            max_retry_attempts (int): The number of retry attempts.
        Returns:
            Tuple[str, str]: The list of formatted log events and the next token
        """
        formatted_events = ""
        for log_events_list in self.stream_cloudwatch_logs(
            events_limit=events_limit, max_retry_attempts=max_retry_attempts
        ):
            formatted_log_events_list = log_events_list.format_messages()
            formatted_events += "\n".join(
                [event.message for event in formatted_log_events_list.events]
            )
        return formatted_events, formatted_log_events_list.next_forward_token
