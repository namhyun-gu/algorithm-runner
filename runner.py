import argparse
import datetime
import os
import subprocess

import yaml
from colored import bg, fg, stylize


def err(message: str):
    print(stylize(message, fg("red")))
    exit(-1)


def padded(message: str):
    for line in message.splitlines():
        print(f"  {line}")


def launch(script: str, tests: list):
    passed = 0
    failed = 0

    for index, test in enumerate(tests):
        index += 1

        input: str = test["input"].rstrip()
        output: str = test["output"].rstrip()

        start_at = datetime.datetime.now()
        process = subprocess.run(
            script, capture_output=True, input=bytes(input, "utf-8"), cwd=cwd
        )
        end_at = datetime.datetime.now()
        elspased = round((end_at - start_at).total_seconds(), 4)
        if process.returncode == 0:
            actual = process.stdout.decode("utf-8").rstrip()
            if actual == output:
                passed += 1
                print(stylize("  PASS  ", fg("white") + bg("green")), end=" ")
                print(f"Test {index}", end=" ")
                print(f"({elspased} ms)")
            else:
                failed += 1
                print(stylize("  FAIL  ", fg("white") + bg("red")), end=" ")
                print(f"Test {index}", end=" ")
                print(f"({elspased} ms)")
                print("\n- Expected\n")
                padded(output)
                print("\n- Actual\n")
                padded(actual)
                print()
        else:
            failed += 1
            print(stylize("  FAIL  ", fg("white") + bg("red")), end=" ")
            print(f"Test {index}", end=" ")
            print(f"({elspased} ms)\n")
            print(process.stderr.decode("utf-8"))

    print(f"\nFinished {len(tests)} tests. (pass: {passed}, fail: {failed})")


parser = argparse.ArgumentParser()
parser.add_argument("config", type=str)
parser.add_argument("--cwd", type=str, default=None)

args = parser.parse_args()

cwd = args.cwd if args.cwd else os.path.dirname(os.path.abspath(args.config))
config = yaml.load(open(args.config), Loader=yaml.FullLoader)

if "script" not in config:
    err("Require 'script' variable in config")

if "tests" not in config:
    err("Require 'tests' variable in config")

script = config["script"]
tests = config["tests"]

if not isinstance(tests, list):
    err("Require 'tests' is list")

if isinstance(script, list):
    for index, s in enumerate(script):
        index += 1

        print(stylize(f"\nLaunch script {index}\n", fg("white")))
        launch(s, tests)
else:
    launch(script, tests)
