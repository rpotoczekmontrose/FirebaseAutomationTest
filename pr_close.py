from helpers import *

pr_number = get_pr_number()
env_name = "PR_" + pr_number
worker_project_id = os.environ[env_name]
set_worker_state(worker_project_id, True)
