"""
Script to run tests with coverage.
"""
import subprocess
import sys
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Run tests with optional coverage")
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage report"
    )
    parser.add_argument(
        "--html", action="store_true", help="Generate HTML coverage report"
    )
    parser.add_argument(
        "--api-only", action="store_true", help="Run only API tests"
    )
    parser.add_argument(
        "--unit-only", action="store_true", help="Run only unit tests"
    )
    parser.add_argument(
        "test_path", nargs="?", default="tests", help="Specify test path to run"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Base command
    if args.coverage:
        cmd = ["pytest", "-xvs"]
    else:
        cmd = ["pytest", "-xvs"]

    # Add markers if specified
    if args.api_only:
        cmd.append("-m")
        cmd.append("api")
    elif args.unit_only:
        cmd.append("-m")
        cmd.append("unit")

    # Add coverage options
    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing"])
        if args.html:
            cmd.append("--cov-report=html")

    # Add test path
    cmd.append(args.test_path)

    # Run the tests
    process = subprocess.Popen(cmd)
    process.communicate()
    return process.returncode


if __name__ == "__main__":
    sys.exit(main())
