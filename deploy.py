"""Register Prefect deployments for the hello-world pipeline."""

from __future__ import annotations

import os
import subprocess
from prefect import flow
from prefect.runner.storage import GitRepository

# Update this URL after you publish your copy of the template
REPO_URL = "https://github.com/NeuroGranberg/hello_world_pipeline.git"
ENTRYPOINT = "flows/hello.py:hello_flow"


def current_sha() -> str:
    """Return the repo SHA for the current working tree."""
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def main() -> None:
    sha = current_sha()
    image = os.environ.get("PIPELINE_IMAGE", f"ghcr.io/your-org/hello-world:{sha}")
    repo = GitRepository(url=REPO_URL, commit_sha=sha)

    flow.from_source(source=repo, entrypoint=ENTRYPOINT).deploy(
        name="hello:docker-cpu",
        work_pool_name="docker-cpu-pool",
        job_variables={"image": image},
    )
    print(f"Registered deployment hello:docker-cpu (pool=docker-cpu-pool, image={image}, sha={sha})")

    flow.from_source(source=repo, entrypoint=ENTRYPOINT).deploy(
        name="hello:local-cpu",
        work_pool_name="local-cpu-pool",
    )
    print(f"Registered deployment hello:local-cpu (pool=local-cpu-pool, sha={sha})")


if __name__ == "__main__":
    main()
