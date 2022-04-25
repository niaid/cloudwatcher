from typing import Optional

import boto3


class CloudWatcher:
    """
    A base class for CloudWatch managers
    """

    def __init__(
        self,
        service_name: str,
        aws_region_name: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
    ) -> None:
        """
        Initialize CloudWatcher

        :param str service_name: The name of the service
        :param str region_name: The name of the region. Defaults to 'us-east-1'
        :param Optional[str] aws_access_key_id: The AWS access key ID
        :param Optional[str] aws_secret_access_key: The AWS secret access key
        :param Optional[str] aws_session_token: The AWS session token
        """
        self.aws_region_name = aws_region_name or "us-east-1"
        self.service_name = service_name
        self.client: boto3.Session.client = boto3.client(
            service_name=self.service_name,
            region_name=self.aws_region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
        )
