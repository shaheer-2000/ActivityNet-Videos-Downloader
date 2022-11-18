import threading

from lib.yt_dl import YoutubeDownloader

# TODO: graceful termination + terminate thread on ctrl + c
# TODO: the batch file needs to be partitioned further for faster downloads on each batch (cpu_count() * 2) partitions

def download_batch_threaded(batch_file, videos_dir, download_archive, logger: "Logger"):
	yt_dl = YoutubeDownloader(videos_dir, download_archive, logger)
	logger.log(f"Downloading youtube videos from {batch_file}")
	yt_dl.download_batch(batch_file)


if __name__ == "__main__":
	from typing import List
	from multiprocessing import cpu_count
	from pathlib import Path
	from os import environ
	from dotenv import load_dotenv

	load_dotenv()

	from lib.logger import Logger
	from lib.google_drive import DriveAPI
	
	logger = Logger(Path("./logs.txt"))

	batches_dir = Path("./batches").resolve()
	if not batches_dir.exists():
		batches_dir.mkdir()

	videos_dir = Path("./videos").resolve()
	if not videos_dir.exists():
		videos_dir.mkdir()

	download_archive = Path("./download_archive.txt").resolve()

	settings = Path("./gdrive.settings.yaml").resolve()
	credentials = Path("./credentials.json").resolve()
	video_folder_id = environ.get("VIDEO_FOLDER_ID")

	gdrive = DriveAPI(settings, credentials, video_folder_id, logger)

	for batch in batches_dir.iterdir():
		threads: List[threading.Thread] = []

		print(f"Creating {len(threads)} threads for the current batch [{batch}]")
		for i in range(cpu_count() * 2):
			threads.append(threading.Thread(target=download_batch_threaded, args=(batch, videos_dir, download_archive, logger)))

		print(f"Starting {len(threads)} threads for the current batch [{batch}]")
		for thread in threads:
			thread.start()
		
		print(f"Waiting for threads to finish for the current batch [{batch}]")
		for thread in threads:
			thread.join()

		print(f"Batch [{batch}] finished downloading...")

		video_files = [f for f in videos_dir.iterdir()]
		
		print(f"{len(video_files)} videos were downloaded for current batch [{batch}]")
		
		gdrive.upload_files(video_files)
