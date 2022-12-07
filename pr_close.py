from helpers import *
import subprocess
import json


def rerun_waiting_job():
    try:
        pr_list = json.loads(
            subprocess.check_output(["gh", "pr", "list", "--json", "number"])
        )
        print(pr_list)
        if len(pr_list) == 0:
            return
        run_to_rerun = None
        for pr in pr_list:
            pr_number = pr["number"]
            checks = str(
                subprocess.check_output(["gh", "pr", "checks", f"{pr_number}"]).decode(
                    "utf-8"
                )
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
    except subprocess.CalledProcessError as error:
        print(error.output)
    except Exception as e:
        print(e)


free_worker()
rerun_waiting_job()
