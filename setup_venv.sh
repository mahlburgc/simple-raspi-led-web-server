#!/bin/bash

VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "Virtual environment not found. Creating one in '$VENV_DIR'..."
  python3 -m venv "$VENV_DIR"
else
  echo "Virtual environment '$VENV_DIR' already exists."
fi

source ./.venv/bin/activate
pip install -r ./requirements.txt