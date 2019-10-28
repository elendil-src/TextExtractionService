import os
import uuid
import boto3
import botocore.exceptions


class S3Storage:
    """
    Manages storage in a given S3 Bucket. Calling client must have required AWS account and
    S3 bucket access permissions
    """

    S3_client = None
    S3_bucket = None
    S3_bucket_region = None

    def __init__(self, bucket_name, bucket_region):
        self.bucket_name = bucket_name
        self.S3_client = boto3.resource('s3')
        self.S3_bucket_region = bucket_region

    def bucket_create_if_not_exist(self):
        """
        Create buckets of given name in caller's AWS context including AWS region. Bucket has private ACL.
        With raise exceptions if call has insufficient AWS permissions
        """
        if self.S3_bucket is None:
            try:
                self.S3_bucket = self.S3_client.create_bucket(
                    ACL='private', Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.S3_bucket_region})
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                    self.S3_bucket = self.S3_client.Bucket(self.bucket_name)

    def bucket_delete(self):
        """
        Delete's bucket. Throws exception if bucket not found or problems accessing bucket
        """
        if self.S3_bucket is not None:
            self.S3_bucket.delete()
            self.S3_bucket = None

    def file_create(self, stream_reader):
        """
        Create unique key, then pass stream of contents to S3 returning the key. Throw S3 exceptions if any problems.
         """
        object_key: str = str(uuid.uuid4())
        object_created = self.S3_bucket.put_object('private', Key=object_key)
        object_created.upload_fileobj(stream_reader)
        return object_key

    def file_read(self, object_key):
        """
        Read and return contents of given file. Throw S3  exception if file not found or cannot be read
        """
        s3_object_ref = self.S3_bucket.Object(object_key)
        s3_object = s3_object_ref.get()
        s3_object_contents = s3_object['Body'].read()
        return s3_object_contents

    def file_delete(self, object_key):
        """
        Delete file; throw exceptions if does not exist if cannot be deleted.
        """
        s3_object = self.S3_client.Object(self.bucket_name, object_key)
        s3_object.delete()


def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)
    statement_image_file = "../ird-test-halifax-cc-statement.jpg"

    # Read document content
    with open(statement_image_file, 'rb') as document:
        image_bytes = bytearray(document.read())

    file_obj = open(statement_image_file, 'rb')

    s3_bucket = S3Storage("elendil.s3storage.main.testbucket", 'eu-west-2')
    print("Constructed class")

    s3_bucket.bucket_create_if_not_exist()
    print("Created bucket")

    object_key = s3_bucket.file_create(file_obj)
    print("Created file=key=" + object_key)

    file_content = s3_bucket.file_read(object_key)
    if file_content != image_bytes:
        raise Exception('contents read from file differ from original')

    print("Read file: contents match original")

    s3_bucket.file_delete(object_key)
    print("Deleted file")

    s3_bucket.bucket_delete()
    print("Deleted bucket")

    print("Test completed successfully")


if __name__ == "__main__":
    main()
