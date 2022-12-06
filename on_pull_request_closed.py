from change_worker_state import *
import os

change_worker_state(os.environ["WORKER_NAME"], True)
