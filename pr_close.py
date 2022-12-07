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
            print(f"pr: {pr}")
            pr_number = pr["number"]
            print(f"curr pr num: {pr_number}")
            decoded = None
            try:
                # for some reason it returns exit code 1 instead of 0...
                subprocess.check_output(["gh", "pr", "checks", f"{pr_number}"])
            except subprocess.CalledProcessError as error:
                decoded = error.output.decode()
            checks = decoded.splitlines()
            print(checks)
            for check in checks:
                if "build_and_preview" in check and "fail" in check:
                    run_to_rerun = check[
                        check.find("runs/") + len("runs/") : check.find("/jobs")
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
