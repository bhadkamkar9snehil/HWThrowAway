from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

BRANCH_PREFIX = "prototype/"


def run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=check,
        text=True,
        capture_output=True,
    )


def remote_job_branches(root: Path) -> list[str]:
    run_git(root, "fetch", "--prune", "origin")
    result = run_git(
        root,
        "for-each-ref",
        "--format=%(refname:short)",
        f"refs/remotes/origin/{BRANCH_PREFIX}*",
    )
    prefix = "origin/"
    return sorted(
        line[len(prefix) :]
        for line in result.stdout.splitlines()
        if line.startswith(prefix + BRANCH_PREFIX)
    )


def queued_job_on_branch(root: Path, branch: str) -> tuple[str, dict] | None:
    listing = run_git(root, "ls-tree", "-r", "--name-only", f"origin/{branch}", "jobs").stdout
    for path in sorted(line.strip() for line in listing.splitlines() if line.strip().endswith(".json")):
        content = run_git(root, "show", f"origin/{branch}:{path}", check=False)
        if content.returncode != 0:
            continue
        try:
            job = json.loads(content.stdout)
        except json.JSONDecodeError:
            continue
        if job.get("status") == "queued":
            return path, job
    return None


def checkout_branch(root: Path, branch: str) -> None:
    run_git(root, "checkout", "--force", "-B", branch, f"origin/{branch}")


def process_job(root: Path, branch: str, job_path: str, job: dict) -> None:
    checkout_branch(root, branch)
    job_file = root / job_path
    job["status"] = "running"
    job_file.write_text(json.dumps(job, indent=2) + "\n", encoding="utf-8")

    env = os.environ.copy()
    env["PROTOTYPE_JOB_ID"] = str(job.get("job_id") or Path(job_path).stem)
    completed = subprocess.run(
        [sys.executable, str(root / "prototype_runner" / "pipeline.py"), "--job", str(job_file)],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
    )

    if completed.returncode == 0:
        job["status"] = "completed"
    elif completed.returncode == 3:
        job["status"] = "completed_with_unknowns"
    else:
        job["status"] = "failed"
    job["runner_exit_code"] = completed.returncode
    job["runner_stdout"] = completed.stdout[-4000:]
    job["runner_stderr"] = completed.stderr[-4000:]
    job["evidence"] = "evidence/latest/summary.json"
    job_file.write_text(json.dumps(job, indent=2) + "\n", encoding="utf-8")

    run_git(root, "add", "-A")
    staged = run_git(root, "diff", "--cached", "--quiet", check=False)
    if staged.returncode != 0:
        message = f"chore(prototype): complete {job.get('job_id', Path(job_path).stem)}"
        run_git(root, "commit", "-m", message)
        # Branch is isolated per design job, so the runner never pushes directly to main.
        run_git(root, "push", "origin", f"HEAD:{branch}")


def poll(root: Path) -> int:
    processed = 0
    for branch in remote_job_branches(root):
        candidate = queued_job_on_branch(root, branch)
        if candidate is None:
            continue
        job_path, job = candidate
        process_job(root, branch, job_path, job)
        processed += 1
    return processed


def main() -> int:
    parser = argparse.ArgumentParser(description="Poll GitHub prototype/* branches and execute queued design jobs.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--interval", type=int, default=30)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    root = args.repo_root.resolve()

    while True:
        try:
            count = poll(root)
            if count:
                print(f"Processed {count} prototype job(s).", flush=True)
        except Exception as exc:
            print(f"Prototype runner error: {exc}", file=sys.stderr, flush=True)
        if args.once:
            break
        time.sleep(max(args.interval, 10))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
