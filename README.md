# vexere-ai-agent

This repo is used for Vexere's interview test only.

# prerequisite

- Java 11 +
- Python 3.11 +

# How to run

- From root directory, `cd  admin-servce` and run `pip install -r requirements.txt` to install packages
- Run `run.py` script with python or make file
  - Python: `python run.py` or `python3 run.py`
  - Make: `make start` or `make start ENVIRONMENT=dev`

==> Only dev environment is avaiable now


# API call
- Api runs with port `1206`
- For chat with agent, POST to `/chat` to interact with model
- For image, POST to `/image` domain