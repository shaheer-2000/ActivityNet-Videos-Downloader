from typing import List
from pathlib import Path
from time import sleep

import youtube_dl
from youtube_dl.utils import DownloadError, SameFileError, ExtractorError, GeoRestrictedError, UnavailableVideoError, UnsupportedError
class YoutubeDownloader:
	def __init__(self, videos_dir: Path, download_archive: Path, logger: "Logger"):
		if not download_archive.exists():
			download_archive.touch()

		self.yt_dl = youtube_dl.YoutubeDL({
			"ignoreerrors": True,
			"outtmpl": (videos_dir / "%(title)s.%(ext)s").as_posix(),
			"verbose": True,
			"download_archive": download_archive
		})

		self.MAX_RETRIES = 10
		self.retries = self.MAX_RETRIES

		self.batch = None

		self.logger = logger

	def load_batch(self, batch_file: Path | None):
		if batch_file is None:
			raise ValueError("No batch_file provided to YoutubeDownloader#load_batch method")
		with open(batch_file, "r") as f:
			self.batch = f.read().splitlines()

	def reset(self):
		self.retries = self.MAX_RETRIES
		self.batch = None

	def download_batch(self, batch_file: Path | None = None, batch: List[str] | None = None):
		if batch_file is None and batch is None:
			raise RuntimeError("Neither batch_file nor batch (as a list of URLs) was provided as an argument")
		if not batch_file is None and not batch is None:
			raise RuntimeError("Both batch_file and batch (as a list of URLs) was provided, when only 1 is accepted")
		if not batch_file is None and self.batch is None:
			self.load_batch(batch_file)
		else:
			self.batch = batch

		try:
			self.yt_dl.download(self.batch)
			# if ret_code != 0:
			# 	raise RuntimeError("Failed to download...")
			self.reset()
		except KeyboardInterrupt as e:
			print("Ctrl+C detected, download interrupted by the user")
			exit(1)
		except Exception as e:
			print(f"There was a problem with the download...\n{e}")
			if self.retries > 0:
				print("Retrying download in 1 minute...")
				sleep(60) # delay by 1 minute
				self.retries -= 1
				self.download_batch()
			else:
				print("Exceeded max number of retries, stopping attempts to download...")

if __name__ == "__main__":
	from logger import Logger

	yt_dl = YoutubeDownloader(Path("./videos").resolve(), Path("./download_archive.txt"), Logger(Path("./logs").resolve()))
	batches = Path("./batches").resolve()

	for batch in batches.iterdir():
		yt_dl.download_batch(batch)
	