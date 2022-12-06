from helpers import *

file1 = open("./.github/variables/myvars.env", "r")
lines = file1.readlines()
print(lines)
pr_number = get_pr_number()
env_name = "PR_" + pr_number
worker_project_id = os.environ[env_name]
set_worker_state(worker_project_id, True)
