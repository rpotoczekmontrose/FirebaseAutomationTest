from google.cloud import firestore_admin_v1
from google.cloud import storage
from google.cloud import firestore
import requests
import os
from base64 import b64encode
from nacl import encoding, public
import json
import subprocess

workers_names = ["testproject2-151a9", "testproject-c1950"]

# [START delete_collection]
def delete_collection(coll_ref, batch_size):

    print(f"Deleting collection: {coll_ref.id}")
    docs = coll_ref.list_documents(page_size=batch_size)
    deleted = 0

    for doc in docs:
        print(f"Deleting doc {doc.id} => {doc.get().to_dict()}")
        doc.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)


# [END delete_collection]


def change_worker_state(worker_name: str, new_state: bool):
    client = firestore.Client(project=worker_name)
    doc = list(client.collection("WorkerAvailability").list_documents())[0]
    doc_dict = doc.get().to_dict()
    doc_dict["isFree"] = new_state
    doc.update(doc_dict)


def get_free_worker_name():
    for worker_name in workers_names:
        client = firestore.Client(project=worker_name)
        doc = list(client.collection("WorkerAvailability").list_documents())[0]
        doc_dict = doc.get().to_dict()
        if doc_dict["isFree"] == True:
            change_worker_state(worker_name, False)
            return worker_name
        else:
            print("Worker: " + worker_name + " busy...")


def export_documents(source_project_id="terra-scouts-us"):
    # Create a client
    client = firestore_admin_v1.FirestoreAdminClient()

    # Initialize request argument(s)
    request = firestore_admin_v1.ExportDocumentsRequest(
        name=f"projects/{source_project_id}/databases/(default)",
        output_uri_prefix=f"gs://{source_project_id}.appspot.com",
    )

    # Make the request
    print("Exporting...")
    operation = client.export_documents(request=request)
    return operation.result().output_uri_prefix


def import_documents(worker_id, input_uri_prefix=""):
    print("Importing...")
    client = firestore_admin_v1.FirestoreAdminClient()
    # for some reason it doesn't work
    request = firestore_admin_v1.ImportDocumentsRequest(
        name=f"projects/{worker_id}/databases/(default)",
        input_uri_prefix=input_uri_prefix,
    )
    operation = client.import_documents(request=request)
    return operation.result()


def db_cleanup(worker_name):
    print("db cleanup")
    db = firestore.Client(project=worker_name)
    for coll_ref in db.collections():
        if "WorkerAvailability" in coll_ref.id:
            continue
        delete_collection(coll_ref, 100)


def backup_cleanup(backup_location: str):
    print("Temporary Backup Cleanup")
    parts = backup_location.split("/")
    time_stamp = parts[len(parts) - 1]
    backup_storage = storage.Client(project="terra-scouts-us")
    bucket = storage.Bucket(backup_storage, "terra-scouts-us.appspot.com")
    for blob in list(bucket.list_blobs()):
        if time_stamp in blob.name:
            print("cleanup backup: " + blob.name)
            blob.delete()


def copy_storage(worker_name):
    print("Copy storage data")
    destination_storage = storage.Client(project=worker_name)
    # use default bucket
    destination_bucket = storage.Bucket(
        destination_storage, worker_name + ".appspot.com"
    )
    # cleanup
    print("Storage cleanup...")
    for blob in list(destination_bucket.list_blobs()):
        print("deleting: " + blob.name)
        blob.delete()
    # copying
    source_bucket = storage.Bucket(destination_storage, "terra-scouts-us.appspot.com")
    for blob in list(source_bucket.list_blobs()):
        print("copying: " + blob.name)
        source_bucket.copy_blob(blob, destination_bucket)


def deploy(worker_project_id):
    subprocess.run(["firebase", "use", worker_project_id])
    output = subprocess.run(
        ["firebase", "deploy", "--only", "hosting"], capture_output=True, stdout=None
    )
    link = output[str(output.stdout).find("Hosting URL:") :]
    print(link)
    print(
        str(
            subprocess.run(
                ["gh", "pr", "comment", "--body", f"{link}"],
                capture_output=True,
                stdout=None,
            ).stdout
        )
    )


print("start")
try:
    worker_name = get_free_worker_name()
    copy_storage(worker_name)
    uri_prefix = export_documents("terra-scouts-us")
    print("uri prefix: " + uri_prefix)
    db_cleanup(worker_name)
    import_documents(worker_name, uri_prefix)
    backup_cleanup(uri_prefix)
    deploy(worker_name)
except:
    if worker_name is not None:
        change_worker_state(worker_name, True)
    else:
        print("No free worker")
        subprocess.run(["gh", "pr", "comment", "--body", "No free worker"])
        exit(1)
