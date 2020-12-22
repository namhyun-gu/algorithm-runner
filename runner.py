import argparse
import os
import subprocess
import time

import yaml
from colored import bg, fg, stylize


def err(message: str):
    print(stylize(message, fg("red")))
    exit(-1)


def padded(message: str):
    for line in message.splitlines():
        print(f"  {line}")


def label(tag: str, message: str, bg_color: str):
    print(stylize(f" {tag.upper()} ", fg("white") + bg(bg_color)), end=" ")
    print(stylize(message, fg("white")))


def run_script(script: str, input: str):
    input = bytes(input, "utf-8")
    start_at = time.time()
    process = subprocess.run(
        script, capture_output=True, input=input, cwd=cwd, timeout=timeout
    )
    end_at = time.time()
    elspased = round((end_at - start_at) * 1000)
    return process, elspased


def launch(script: str, tests: list):
    passed = 0
    total_time = 0

    print(stylize(f"\n* Run '{script}'\n", fg("white")))

    for index, test in enumerate(tests):
        index += 1

        input: str = test["input"].rstrip()
        output: str = test["output"].rstrip()

        try:
            process, elspased = run_script(script, input)

            total_time += elspased

            if process.returncode == 0:
                actual = process.stdout.decode("utf-8").rstrip()
                if actual == output:
                    passed += 1
                    label("pass", f"Test Case {index} ({elspased}ms)", "green")
                else:
                    label("fail", f"Test Case {index} ({elspased}ms)", "red")
                    print("\n- Input\n")
                    padded(input)
                    print("\n- Expected\n")
                    padded(stylize(output, fg("green")))
                    print("\n- Actual\n")
                    padded(stylize(actual, fg("red")))
                    print()
            else:
                label("fail", f"Test Case {index} ({elspased}ms)", "red")
                print("\n- Input\n")
                padded(input)
                print()
                print(stylize(process.stderr.decode("utf-8"), fg("red")))
        except subprocess.TimeoutExpired:
            total_time += timeout * 1000

            label("fail", f"Test Case {index} ({timeout}s)", "red")
            print("\n- Input\n")
            padded(input)
            print(stylize("\nTimeoutExpired\n", fg("red")))
    print(
        "Tests:\t" + stylize(f"{passed} passed", fg("green")) + f", {len(tests)} total"
    )
    print(f"Time:\t{round(total_time / 1000, 3)}s\n")


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
timeout = config["timeout"] if "timeout" in config else None

if not isinstance(tests, list):
    err("Require 'tests' is list")

if timeout and not isinstance(timeout, int):
    err("Require 'timeout' is int")

if not isinstance(script, list):
    script = [script]

for s in script:
    launch(s, tests)