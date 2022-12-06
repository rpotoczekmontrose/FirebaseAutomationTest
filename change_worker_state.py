from google.cloud import firestore


def change_worker_state(worker_name: str, new_state: bool):
    client = firestore.Client(project=worker_name)
    doc = list(client.collection("WorkerAvailability").list_documents())[0]
    doc_dict = doc.get().to_dict()
    doc_dict["isFree"] = new_state
    doc.update(doc_dict)
