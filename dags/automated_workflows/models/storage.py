import json


class Storage:
    def __init__(self,
        conn_id : str = "aws_default",
        bucket : str = "astro-sandbox-data",
        config_file : str = "automated-workflows.json"
    ):
        self.conn_id : str = conn_id
        self.bucket : str = bucket
        self.config_file : str = config_file


    def read(self):
        import json
        from io import StringIO
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        from botocore.exceptions import ClientError

        s3_hook = S3Hook(aws_conn_id=self.conn_id)
        try:
            file_data = StringIO(
                s3_hook.read_key(
                    key=self.config_file,
                    bucket_name=self.bucket
                )
            )
            return json.loads(
                str(file_data.read())
            )
        except ClientError as e:
            import logging
            logging.error(e)
            return []

    def save(self, config:str):
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook

        s3_hook = S3Hook(aws_conn_id=self.conn_id)
        s3_hook.load_string(
            json.dumps(config),
            self.config_file,
            bucket_name=self.bucket,
            replace=True
        )

    def remove(self):
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook

        s3_hook = S3Hook(aws_conn_id=self.conn_id)
        s3_hook.delete_object(
            bucket=self.bucket,
            keys=[self.config_file]
        )

