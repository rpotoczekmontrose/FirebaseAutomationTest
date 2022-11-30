from google.cloud import firestore_admin_v1
from google.cloud import storage
from google.cloud import firestore

# [START delete_collection]
def delete_collection(coll_ref, batch_size):
    docs = coll_ref.list_documents(page_size=batch_size)
    deleted = 0

    for doc in docs:
        print(f"Deleting doc {doc.id} => {doc.get().to_dict()}")
        doc.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)


# [END delete_collection]


def export_documents(project_id="testproject-c1950"):
    # Create a client
    client = firestore_admin_v1.FirestoreAdminClient()

    # Initialize request argument(s)
    request = firestore_admin_v1.ExportDocumentsRequest(
        name=f"projects/{project_id}/databases/(default)",
        output_uri_prefix="gs://testproject-c1950.appspot.com",
    )

    # Make the request
    print("Exporting...")
    operation = client.export_documents(request=request)
    return operation.result().output_uri_prefix


def import_documents(project_id="terra-scouts-us", input_uri_prefix=""):
    print("Importing...")
    client = firestore_admin_v1.FirestoreAdminClient()
    # for some reason it doesn't work
    request = firestore_admin_v1.ImportDocumentsRequest(
        name=f"projects/{project_id}/databases/(default)",
        input_uri_prefix=input_uri_prefix,
    )
    client.import_documents(request=request)


def db_cleanup():
    print("db cleanup")
    db = firestore.Client(project="terra-scouts-us")

    for coll_ref in db.collections():
        delete_collection(coll_ref, 100)


def backup_cleanup(backup_location: str):
    print("Storage Cleanup")
    parts = backup_location.split("/")
    time_stamp = parts[len(parts) - 1]
    backup_storage = storage.Client(project="testproject-c1950")
    bucket = storage.Bucket(backup_storage, "testproject-c1950.appspot.com")
    for blob in list(bucket.list_blobs()):
        if time_stamp in blob.name:
            print("cleanup backup: " + blob.name)
            blob.delete()


def copy_storage():
    print("Copy storage data")
    destination_storage = storage.Client(project="terra-scouts-us")
    # use default bucket
    destination_bucket = storage.Bucket(
        destination_storage, "terra-scouts-us.appspot.com"
    )
    # cleanup
    print("Storage cleanup...")
    for blob in list(destination_bucket.list_blobs()):
        print("deleting: " + blob.name)
        blob.delete()
    # copying
    source_bucket = storage.Bucket(destination_storage, "testproject-c1950.appspot.com")
    for blob in list(source_bucket.list_blobs()):
        print("copying: " + blob.name)
        source_bucket.copy_blob(blob, destination_bucket)


print("start")
copy_storage()
uri_prefix = export_documents("testproject-c1950")
print("uri prefix: " + uri_prefix)
db_cleanup()
import_documents("terra-scouts-us", uri_prefix)
backup_cleanup(uri_prefix)
