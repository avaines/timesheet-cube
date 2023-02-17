#!/bin/bash

# Create new virtualenv
VIRTUALENV_PATH=".venv"

if [[ ! -d "${VIRTUALENV_PATH}" ]]; then
    echo "${VIRTUALENV_PATH} does not currently exist, creating virtual environment"
    python3 -m venv "${VIRTUALENV_PATH}"
    python3 -m venv "${VIRTUALENV_PATH}" --upgrade
fi

echo "Activtating ${VIRTUALENV_PATH} virtual environment"
source "${VIRTUALENV_PATH}/bin/activate"

echo "Installing PIP requirements"
pip3 install -r requirements.txt

if [[ -f .env ]]; then
    echo "Exposing Environmental Variables"
    source .env
fi

python3 main.py
