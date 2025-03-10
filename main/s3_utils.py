"""Amazon S3 image uploading."""

import boto3
from botocore.exceptions import ClientError
from flask import current_app


def init_s3():
    """Initialise the S3 client."""
    return boto3.client(
        's3',
        region_name=current_app.config['AWS_REGION'],
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['AWS_SECRET_KEY'],
        config=boto3.session.Config(signature_version='s3v4')
    )


def upload_s3(file, filename, folder=None, private=False):
    """Upload a file to S3 and return the URL."""
    s3 = init_s3()
    bucket = current_app.config['AWS_BUCKET']

    try:
        filepath = f'{folder}/{filename}' if folder else filename
        
        # Set extra args based on whether the file should be private
        extra_args = {
            'ContentType': file.content_type
        }
        
        # Only add ACL for public files
        if not private:
            extra_args['ACL'] = 'public-read'
        
        s3.upload_fileobj(
            file,
            bucket,
            filepath,
            ExtraArgs=extra_args
        )
        
        # For private files, just return the filepath since we'll generate presigned URLs later
        if private:
            return filepath
        
        # For public files, return the full URL
        return f'https://{bucket}.s3.amazonaws.com/{filepath}'
    except ClientError as e:
        print(e)
        return None