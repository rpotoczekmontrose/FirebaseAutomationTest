from helpers import *
import subprocess
import json


def rerun_waiting_job():
    pr_list = json.loads(
        subprocess.run(
            ["gh", "pr", "list", "--json", "number"],
            capture_output=True,
            stdout=None,
        ).stdout
    )
    if len(pr_list) == 0:
        return
    run_to_rerun = ""
    for pr in pr_list:
        pr_number = pr["number"]
        checks = str(
            subprocess.run(
                ["gh", "pr", "checks", f"{pr_number}"],
                capture_output=True,
                stdout=None,
            ).stdout
        ).splitlines()
        for check in checks:
            if "build_and_preview" in check and "fail" in check:
                run_to_rerun = check[
                    check.find("runs/") + len("runs/") + 1 : check.find("/jobs") - 1
                ]
                break
            else:
                continue
    output = subprocess.run(
        ["gh", "run", "rerun", f"{run_to_rerun}"],
        capture_output=True,
    )
    print(output.stdout)
    print(output.stderr)


free_worker()
rerun_waiting_job()
