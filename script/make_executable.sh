#!/bin/sh

# Enter venv
.venv/Scripts/activate

# Run pyinstaller
pyinstaller --onefile runner.py