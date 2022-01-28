from google.cloud import storage


def upload_to_bucket(blob_name, path_to_file, bucket_name):
    """ Upload data to a bucket"""

    # Explicitly use service account credentials by specifying the private key
    # file.
    storage_client = storage.Client.from_service_account_json('./credentials.json')

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.upload_from_filename(path_to_file)


    #blob.upload_from_string(
    #                        uploaded_file.read(),
    #                        content_type=uploaded_file.content_type)

    #returns a public url
    return blob.public_url


def registrar_na_gcp(buffer, bucket, filename):
    storage_client = storage.Client.from_service_account_json('./credentials.json')
    bucket = storage_client.get_bucket(bucket)
    blob = bucket.blob(filename)
    blob.upload_from_string(buffer.getvalue(),content_type='application/xml')

