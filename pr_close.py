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
    print(pr_list)
    if len(pr_list) == 0:
        return
    run_to_rerun = None
    for pr in pr_list:
        pr_number = pr["number"]
        checks = str(
            subprocess.run(
                ["gh", "pr", "checks", f"{pr_number}"],
                capture_output=True,
                stdout=None,
            ).stdout
        ).splitlines()
        print(checks)
        for check in checks:
            if "build_and_preview" in check and "fail" in check:
                run_to_rerun = check[
                    check.find("runs/") + len("runs/") + 1 : check.find("/jobs") - 1
                ]
                print(run_to_rerun)
                break
            else:
                continue
    if run_to_rerun is None:
        print("Nothing to rerun")
        return
    output = subprocess.run(
        ["gh", "run", "rerun", f"{run_to_rerun}"],
        capture_output=True,
    )
    print(output.stdout)
    print(output.stderr)


free_worker()
rerun_waiting_job()
