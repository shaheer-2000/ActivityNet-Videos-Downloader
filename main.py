import threading

from lib.yt_dl import YoutubeDownloader

# TODO: graceful termination + terminate thread on ctrl + c

def download_batch_threaded(batch_file, start_index, batch, videos_dir, download_archive, logger: "Logger"):
	yt_dl = YoutubeDownloader(videos_dir, download_archive, logger)
	logger.log(f"Thread {threading.get_ident()} is downloading youtube videos from {batch_file.stem}_{start_index}-{start_index + len(batch)}")
	yt_dl.download_batch(batch=batch)
	logger.log(f"Thread {threading.get_ident()} has finished downloading youtube videos from {batch_file.stem}_{start_index}-{start_index + len(batch)}")


if __name__ == "__main__":
	from typing import List
	from multiprocessing import cpu_count
	from pathlib import Path
	from os import environ
	from dotenv import load_dotenv
	from math import ceil
	import zipfile
	import sys
	from time import sleep

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
		flags = [flag for flag in sys.argv[1:]]

		if not len(flags) or "-d" in flags:
			threads: List[threading.Thread] = []

			batch_urls = None
			with open(batch, "r") as f:
				batch_urls = f.readlines()

			batch_partition_size = ceil(len(batch_urls) / batch_partition_count)
			batches_of_batch_urls = []

			downloaded_urls = []
			with open(download_archive, "r") as f:
				downloaded_urls = list(map(lambda x: x.split(" ")[1], f.readlines()))

			batch_urls_count = len(batch_urls)
			for i in range(batch_partition_count):
				start_index = i * batch_partition_size
				end_index = min(batch_urls_count, start_index + batch_partition_size)
				batches_of_batch_urls.append(list(filter(lambda x: not x.split("watch?v=")[1] in downloaded_urls, batch_urls[start_index:end_index])))

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
		
		if not len(flags) or "-d" in flags:
			print(f"{len(video_files)} videos were downloaded for current batch [{batch}]")

		if len(flags) and "-z" in flags:
			## Zip the current batch's video files
			print(f"Zipping video files downloaded for current batch [{batch}]")

			archived_batch_name = f"{batch.stem}.zip"
			if not archived_batch_name in archived_batches:
				with zipfile.ZipFile(archive_dir / archived_batch_name, "w") as archive:
					for f in video_files:
						archive.write(f)
			
			# print(f"Uploading compressed video files [{archived_batch_name}] to Google Drive")

		if not len(flags) or "-u" in flags:
			## Upload current batch's video files
			print(f"Uploading video files for the current batch [{batch}]")

			keep_restarting_upload = True
			upload_retry_count = 0

			while (keep_restarting_upload):
				try:
					# uploading the archive
					# gdrive.upload_files([(archive_dir / archived_batch_name).resolve().as_posix()]) # archived uploading
					# uploading entire batch
					gdrive.upload_files(video_files) # to mitigate connection issues
					upload_retry_count = 0 # reset count if succeeds
					"""
					# batching video files for upload
					video_files_count = len(video_files)
					video_upload_batch_size = 5
					for i in range(0, video_files_count, video_upload_batch_size):
						gdrive.upload_files(video_files[i:min(i+video_upload_batch_size, video_files_count)])
					"""
				except Exception as e:
					print(f"There was an issue while uploading to Google Drive, current batch is [{batch}]\n{e}")
					print("Automatically restarting upload in 1 minute\nYou can kill this process using Ctrl+C")
					upload_retry_count += 1
					sleep(60)
					"""
					# if upload retries exceed threshold, do some operation here
					if upload_retry_count > 5:
						# do some operation here
						pass
					"""
					"""
					print(f"Do you want to restart the upload process? (it'll resume from where it left off) [y/N]: ")
					if input().lower() != "y":
						keep_restarting_upload = False
						print("Exiting gracefully")
						exit(1)
					"""

		if len(flags) and "-r" in flags:
			# empty videos folder here
			# no check to ensure whether all files uploaded successfully or not.
			# run this very carefully to preserve work
			for f in video_files:
				f.unlink(missing_ok=True)
