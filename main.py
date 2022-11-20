import threading

from lib.yt_dl import YoutubeDownloader

# TODO: graceful termination + terminate thread on ctrl + c
# TODO: the batch file needs to be partitioned further for faster downloads on each batch (cpu_count() * 2) partitions

def download_batch_threaded(batch_file, start_index, batch, videos_dir, download_archive, logger: "Logger"):
	yt_dl = YoutubeDownloader(videos_dir, download_archive, logger)
	logger.log(f"Thread {threading.get_ident()} is downloading youtube videos from {batch_file}_{start_index}-{start_index + len(batch)}")
	yt_dl.download_batch(batch=batch)
	logger.log(f"Thread {threading.get_ident()} has finished downloading youtube videos from {batch_file}_{start_index}-{start_index + len(batch)}")


if __name__ == "__main__":
	from typing import List
	from multiprocessing import cpu_count
	from pathlib import Path
	from os import environ
	from dotenv import load_dotenv
	from math import ceil
	import zipfile

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

	archive_dir = Path("./archive").resolve()
	if not archive_dir.exists():
		archive_dir.mkdir()

	archived_batches = [f.resolve().name for f in archive_dir.iterdir()]

	download_archive = Path("./download_archive.txt").resolve()

	settings = Path("./gdrive.settings.yaml").resolve()
	credentials = Path("./credentials.json").resolve()
	video_folder_id = environ.get("VIDEO_FOLDER_ID")

	gdrive = DriveAPI(settings, credentials, video_folder_id, logger)

	max_threads = cpu_count() * 2
	batch_partition_count = max_threads

	for batch in batches_dir.iterdir():
		threads: List[threading.Thread] = []

		batch_urls = None
		with open(batch, "r") as f:
			batch_urls = f.readlines()

		batch_partition_size = ceil(len(batch_urls) / batch_partition_count)
		batches_of_batch_urls = []

		for i in range(batch_partition_count):
			start_index = i * batch_partition_size
			end_index = start_index + batch_partition_size
			batches_of_batch_urls.append(batch_urls[start_index:end_index])

		print(f"Creating {len(threads)} threads for the current batch [{batch}]")
		for i in range(max_threads):
			threads.append(threading.Thread(target=download_batch_threaded, args=(batch, i, batches_of_batch_urls[i], videos_dir, download_archive, logger), daemon=True))

		print(f"Starting {len(threads)} threads for the current batch [{batch}]")
		for thread in threads:
			thread.start()
		
		print(f"Waiting for threads to finish for the current batch [{batch}]")
		for thread in threads:
			thread.join()

		print(f"Batch [{batch}] finished downloading...")

		video_files = [f.resolve() for f in videos_dir.iterdir()]
		
		print(f"{len(video_files)} videos were downloaded for current batch [{batch}]")

		## Zip the current batch's video files
		"""
		print(f"Zipping video files downloaded for current batch [{batch}]")

		archived_batch_name = f"{batch.stem}.zip"
		if not archived_batch_name in archived_batches:
			with zipfile.ZipFile(archive_dir / archived_batch_name, "w") as archive:
				for f in video_files:
					archive.write(f)
		
		# print(f"Uploading compressed video files [{archived_batch_name}] to Google Drive")
		"""

		## Upload current batch's video files
		print(f"Uploading video files for the current batch [{batch}]")

		try:
			# gdrive.upload_files([(archive_dir / archived_batch_name).resolve().as_posix()]) # archived uploading
			gdrive.upload_files(video_files)
		except Exception as e:
			print(f"There was an issue while uploading to Google Drive, current batch is [{batch}]\n{e}\nExitting gracefully")
			exit(1)

		# empty videos folder here
		# no check to ensure whether all files uploaded successfully or not.
		# run this very carefully to preserve work
		for f in video_files:
			f.unlink(missing_ok=True)
