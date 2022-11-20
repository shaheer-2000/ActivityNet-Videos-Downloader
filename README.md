# FYP-Dataset-Downloader
## Installation
- Navigate to the project directory
- `pip install poetry`
- `poetry config virtualenvs.in-project true`
- `poetry install`

## Usage
- Copy the `client_secret.json` and `.env` file to the project directory
- **IF** the following folders (`/videos`, `/batches`) don't exist, create them
- Copy all of your pre-specified batches (from GoogleDrive folder) to the `/batches` directory
- On the first run, you will be prompted to give access to GDrive on your browser, accept that
- `poetry shell`
- `poetry run python main.py`

## Note
- Please actively monitor and report bugs
