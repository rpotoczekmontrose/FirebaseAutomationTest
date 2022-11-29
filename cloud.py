import firebase_admin
import requests
import sys
import subprocess
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage
from google.cloud import firestore_admin_v1
from google.cloud import client

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
        input_uri_prefix=backup_location;
    )
    operation = client.import_documents(request=request)
    print(operation.result())
    # token = (
    #     subprocess.check_output(["gcloud", "auth", "print-access-token"], shell=True)
    #     .decode(sys.stdout.encoding)
    #     .strip()
    # )

    # response = requests.post(
    #     url=f"https://datastore.googleapis.com/v1/projects/{project_id}:import",
    #     json={"inputUrl": backup_location},
    #     headers={"Authorization": f"Bearer {token}"},
    # )


def db_cleanup(app):
    print("DB Cleanup")
    db = firestore.client(app)

    for coll_ref in db.collections():
        delete_collection(coll_ref, 100)


def backup_cleanup(app):
    print("Storage Cleanup")
    bucket = storage.bucket(app=app)
    li = list(bucket.list_blobs())
    print(li)
    bucket.delete_blobs(li)


print("start")
# Use a service account.
terra_app = firebase_admin.initialize_app(
    name="backup",
    options={
        "projectId": "testproject-c1950",
        "storageBucket": "testproject-c1950.appspot.com",
    },
)
backup_cleanup(terra_app)
backup_location = export_documents("testproject-c1950")
#backup_location = f"gs://testproject-c1950.appspot.com/{list(storage.bucket(app=terra_app).list_blobs())[0].name}"

terra_app = firebase_admin.initialize_app(
    name="worker", options={"projectId": "terra-scouts-us"}
)

db_cleanup(terra_app)
import_documents("terra-scouts-us", backup_location)
