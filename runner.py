import argparse
import os
import subprocess
import time
from dataclasses import dataclass

import yaml
from rich.console import Console
from rich.table import Table
from rich import traceback

@dataclass
class TestCase:
    input: str
    output: str


@dataclass
class Context:
    timeout: int = None
    workdir: str = None


@dataclass
class Config:
    scripts: list[any]
    tests: list[TestCase]
    context: Context


def run_script(context: Context, script: str, input: str):
    input = bytes(input, "utf-8")
    start_at = time.time()
    process = subprocess.run(
        script,
        capture_output=True,
        input=input,
        cwd=context.workdir,
        timeout=context.timeout,
    )
    end_at = time.time()
    elspased = round((end_at - start_at) * 1000)
    return process, elspased


def launch(context: Context, script: str, tests: list):
    passed = 0
    total_time = 0

    with console.status("Run tests..."):
        for index, test in enumerate(tests):
            index += 1

            input: str = test["input"].rstrip()
            output: str = test["output"].rstrip()

            table = Table(show_header=False, show_edge=False, show_lines=True)

            try:
                process, elspased = run_script(context, script, input)

                total_time += elspased

                if process.returncode == 0:
                    actual = process.stdout.decode("utf-8").rstrip()
                    if actual == output:
                        passed += 1

                        print_pass(f"Test Case {index} ({elspased}ms)")
                    else:
                        print_fail(f"Test Case {index} ({elspased}ms)\n")

                        table.add_row("Input", input)
                        table.add_row("Expected", f"[green]{output}")
                        table.add_row("Actual", f"[red]{actual}")
                        console.print(table, "\n")
                else:
                    stderr = process.stderr.decode("utf-8")

                    print_fail(f"Test Case {index} ({elspased}ms)\n")

                    table.add_row("Input", input)
                    table.add_row("Error", f"[red]{stderr.strip()}")
                    console.print(table, "\n")

            except subprocess.TimeoutExpired:
                total_time += context.timeout * 1000

                print_fail(f"Test Case {index} ({context.timeout}s)\n")

                table.add_row("Input", input)
                table.add_row("Error", f"[red]TimeoutExpired")
                console.print(table, "\n")

        print_summary(passed, len(tests), round(total_time / 1000, 3))


def print_pass(message: str):
    console.print(
        f"[on green] PASS [/on green] {message}", style="white", highlight=False
    )


def print_fail(message: str):
    console.print(f"[on red] FAIL [/on red] {message}", style="white", highlight=False)


def print_summary(passed: int, total: int, elspaed_time: float):
    summary = f"\nTests:\t[green]{passed} passed[/green], {total} total\nTime:\t{elspaed_time}s"

    console.print(summary, style="white", highlight=False)


def err(message: str):
    console.print(f"[red]{message}[/red]")
    exit(1)


def load_config(path: str) -> Config:
    config = yaml.load(open(path), Loader=yaml.FullLoader)

    scripts = (
        config["script"]
        if "script" in config
        else err("Require [bold]'script'[/bold] variable in config")
    )

    if isinstance(scripts, str):
        scripts = [scripts]

    if not (isinstance(scripts, list) or isinstance(scripts, str)):
        err("Require [bold]'script'[/bold] is [bold]string or list[/bold]")

    tests = (
        config["tests"]
        if "tests" in config
        else err("Require [bold]'tests'[/bold] variable in config")
    )

    if not isinstance(tests, list):
        err("Require [bold]'tests'[/bold] is list")

    context = Context()

    if "context" in config:
        context = config["context"]

        timeout = context["timeout"] if "timeout" in context else None

        if timeout and not isinstance(timeout, int):
            err("Require [bold]'timeout'[/bold] is int")

        workdir = (
            context["workdir"]
            if "workdir" in context
            else os.path.dirname(os.path.abspath(path))
        )

        context = Context(timeout=timeout, workdir=workdir)

    return Config(scripts=scripts, tests=tests, context=context)


def run_config(config: Config):
    for script in config.scripts:
        launch(config.context, script, config.tests)


if __name__ == "__main__":
    traceback.install()

    console = Console()

    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=str)

    args = parser.parse_args()

    config = load_config(args.config)
    run_config(config)