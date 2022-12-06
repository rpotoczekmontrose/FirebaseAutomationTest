from google.cloud import firestore
import os


def set_worker_state(worker_name: str, is_free: bool):
    client = firestore.Client(project=worker_name)
    doc = list(client.collection("WorkerAvailability").list_documents())[0]
    doc_dict = doc.get().to_dict()
    doc_dict["isFree"] = is_free
    doc.update(doc_dict)


def get_pr_number() -> str:
    parts = os.environ["GITHUB_REF"].split("/")
    # refs/pull/:prNumber/merge
    # number should be on position 2
    pr_number = parts[2]
    print(f"pr_number: {pr_number}")
    return pr_number
