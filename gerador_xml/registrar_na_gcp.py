from google.cloud import storage
import json


def upload_to_bucket(blob_name, path_to_file, bucket_name):
    """ Upload data to a bucket"""

    # Explicitly use service account credentials by specifying the private key
    # file.
    storage_client = storage.Client.from_service_account_json('./credentials.json')

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.upload_from_filename(path_to_file)

    return blob.public_url


def registrar_na_gcp(content, bucket, filename, type):
    '''Registra infos (xml, csv ou json) na gcp'''

    storage_client = storage.Client.from_service_account_json('./credentials.json')
    bucket = storage_client.get_bucket(bucket)
    blob = bucket.blob(filename)
    if type == 'xml':
        data = content.getvalue()
        content_type='application/xml'
    elif type == 'csv':
        data = content.getvalue()
        content_type='text/csv'
    elif type == 'json':
        data = json.dumps(content, default=str)
        content_type='application/json'
    blob.upload_from_string(data, content_type)

    return blob.public_url
