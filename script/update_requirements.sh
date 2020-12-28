#!/bin/sh

# Enter venv
.venv/Scripts/activate

# Update requirements.txt
pip freeze > requirements.txt

# Staging updated requirements.txt
git add requirements.txt