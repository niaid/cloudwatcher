# Login credentials

The login credentials that determine the AWS account to be used are resolved by [`boto3`](https://boto3.amazonaws.com), the official Python SDK for AWS, during the `boto3.Session.client` initialization.

## Resolution order

In general, the credentials are resolved in the following order:

1. The credentials are read from the environment variables:
    - `AWS_ACCESS_KEY_ID`
    - `AWS_SECRET_ACCESS_KEY`

    ```console
    export AWS_ACCESS_KEY_ID=<access_key_id>
    export AWS_SECRET_ACCESS_KEY=<secret_access_key>
    ```

2. The credentials are read from `[default]` section of the `~/.aws/credentials` file

    ```console
    [default]
    aws_access_key_id = <access_key_id>
    aws_secret_access_key = <secret_access_key>
    ```
