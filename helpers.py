from google.cloud import firestore
import os

workers_names = ["testproject-c1950", "testproject2-151a9"]


def _set_worker_data(worker_name: str, pr_number: int):
    client = firestore.Client(project=workers_names[0])
    doc = list(client.collection("WorkerAvailability").list_documents())[0]
    doc_dict = doc.get().to_dict()
    doc_dict["workersData"][worker_name] = pr_number
    doc.update(doc_dict)


def _get_workers_dict():
    client = firestore.Client(project=workers_names[0])
    doc = list(client.collection("WorkerAvailability").list_documents())[0]
    doc_dict = doc.get().to_dict()
    return doc_dict["workersData"]


def free_worker():
    current_pr_number = get_pr_number()
    for worker_name, pr_number in _get_workers_dict().items():
        if pr_number == current_pr_number:
            set_worker_state(worker_name, True)


def set_worker_state(worker_name: str, is_free: bool):
    client = firestore.Client(project=worker_name)
    doc = list(client.collection("WorkerAvailability").list_documents())[0]
    doc_dict = doc.get().to_dict()
    doc_dict["isFree"] = is_free
    doc.update(doc_dict)
    _set_worker_data(worker_name, -1 if is_free is True else get_pr_number())


def get_pr_number() -> int:
    os_num = os.environ["PR_NUMBER"]
    print(f"pr_num: {os_num}")
    parts = os.environ["GITHUB_REF"].split("/")
    # refs/pull/:prNumber/merge
    # number should be on position 2
    pr_number = parts[2]
    print(f"pr_number: {pr_number}")
    return int(pr_number)


def _get_free_worker_name():
    for worker_name, pr_number in _get_workers_dict().items():
        if pr_number != -1:
            print("Worker: " + worker_name + " busy...")
            continue
        client = firestore.Client(project=worker_name)
        doc = list(client.collection("WorkerAvailability").list_documents())[0]
        doc_dict = doc.get().to_dict()
        if doc_dict["isFree"] == True:
            set_worker_state(worker_name, False)
            return worker_name


def get_worker_name():
    current_pr_number = get_pr_number()
    for worker_name, pr_number in _get_workers_dict().items():
        if pr_number == current_pr_number:
            return worker_name
    return _get_free_worker_name()
