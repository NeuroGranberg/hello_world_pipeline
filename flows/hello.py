"""Hello-world Prefect flow demonstrating the NILS pipeline conventions."""

from __future__ import annotations

import argparse
from prefect import flow, task, get_run_logger


@task(name="greet")
def greet(name: str) -> str:
    """Construct a greeting for the provided name."""
    return f"Hello, {name}!"


@task(name="detect_environment")
def detect_environment() -> str:
    """Report which runtime environment the pipeline is executing in."""
    import os

    if os.getenv("KUBERNETES_SERVICE_HOST"):
        return "kubernetes"
    if os.path.exists("/.dockerenv"):
        return "docker"
    return "local"


@flow(name="hello-flow", log_prints=True)
def hello_flow(name: str = "World") -> None:
    """Minimal flow that logs a friendly greeting and the active runtime."""
    logger = get_run_logger()
    message = greet(name)
    environment = detect_environment()
    logger.info(f"{message} (running on {environment})")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Execute the hello-world Prefect flow")
    parser.add_argument("--name", default="World", help="Name to include in the greeting")
    return parser


if __name__ == "__main__":
    args = _build_parser().parse_args()
    hello_flow(name=args.name)
