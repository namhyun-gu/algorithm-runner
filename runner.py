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
    process = subprocess.run(script, capture_output=True, input=input, cwd=cwd)
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
            print()
            print(process.stderr.decode("utf-8"))

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

if not isinstance(tests, list):
    err("Require 'tests' is list")

if isinstance(script, list):
    for index, s in enumerate(script):
        index += 1

        print(stylize(f"\nLaunch script {index}\n", fg("white")))
        launch(s, tests)
else:
    launch(script, tests)
