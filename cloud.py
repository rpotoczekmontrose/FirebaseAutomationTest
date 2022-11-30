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


def import_documents(project_id="terra-scouts-us", backup_location=""):
    print("Importing...")
    client = firestore_admin_v1.FirestoreAdminClient()
    # for some reason it doesn't work
    request = firestore_admin_v1.ImportDocumentsRequest(
        name=f"projects/{project_id}/databases/(default)",
        input_uri_prefix=backup_location,
    )
    client.import_documents(request=request)


def db_cleanup():
    db = firestore.Client(project="terra-scouts-us")

    for coll_ref in db.collections():
        delete_collection(coll_ref, 100)


def backup_cleanup(backup_location):
    print("Storage Cleanup")
    backup_storage = storage.Client(project="testproject-c1950")
    bucket = storage.Bucket(backup_storage, "testproject-c1950.appspot.com")
    print(backup_location)
    # bucket.get_blob(backup_location).delete()


def copy_storage():
    destination_storage = storage.Client(project="terra-scouts-us")
    # use default bucket
    destination_bucket = storage.Bucket(
        destination_storage, "terra-scouts-us.appspot.com"
    )
    # cleanup
    for blob in list(destination_bucket.list_blobs()):
        blob.delete()
    # copying
    source_bucket = storage.Bucket(destination_storage, "testproject-c1950.appspot.com")
    for blob in list(source_bucket.list_blobs()):
        source_bucket.copy_blob(blob, destination_bucket)


print("start")
# Use a service account.

copy_storage()
backup_location = export_documents("testproject-c1950")
db_cleanup()
import_documents("terra-scouts-us", backup_location)
backup_cleanup(backup_location)
