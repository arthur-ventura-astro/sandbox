resource "aws_iam_user" "airflow_xcom" {
  name = "airflow-xcom"
  force_destroy = true
}

resource "aws_iam_access_key" "airflow_xcom" {
  user = aws_iam_user.airflow_xcom.name
}

resource "local_file" "key_pair" {
  content  = "${aws_iam_access_key.airflow_xcom.id},${aws_iam_access_key.airflow_xcom.secret}"
  filename = ".secrets/keys.txt"
}

resource "aws_iam_user_policy" "airflow_xcom" {
  name = "AirflowXComBackendAWSS3"
  user = aws_iam_user.airflow_xcom.name
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "s3:ReplicateObject",
          "s3:PutObject",
          "s3:GetObject",
          "s3:RestoreObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ],
        "Resource" : [
          "arn:aws:s3:::${module.data.xcom_bucket}/*",
          "arn:aws:s3:::${module.data.xcom_bucket}"
        ]
      }
    ]
  })
}
