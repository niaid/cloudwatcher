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

        Args:
            service_name (str): The name of the service to use
            aws_region_name (Optional[str]): The AWS region name. Defaults to 'us-east-1'
            aws_access_key_id (Optional[str]): The AWS access key ID. Defaults to None
            aws_secret_access_key (Optional[str]): The AWS secret access key. Defaults to None
            aws_session_token (Optional[str]): The AWS session token. Defaults to None
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
