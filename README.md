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

### Usage Tips
- You can limit or perform extra operations along with the script by specifying flags (`-u`, `-d`, `-z`, `-r`)
- `-u` only uploads all the files present in the `/videos` directory (this happens if no flag is specified)
- `-d` only downloads all the video files from the batches (this happens if no flag is specified)
- `-z` zips the video files into a compressed archive and stores in the `/archive` directory
- `-r` deletes all the video files
- If you only specify `-z` or specify no flags at all, the default process is to `download` -> `upload` for all batches
### Usage Example
- To follow the default process
```
poetry run python main.py
```
- To follow the default process and zip all video files
```
poetry run python main.py -z
```
- To only upload files
```
poetry run python main.py -u
```
- To follow the default process and delete all video files
```
poetry run python main.py -r
```

## Note
- Please actively monitor and report bugs
