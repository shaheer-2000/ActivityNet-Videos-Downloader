from pathlib import Path
from datetime import datetime

class Logger:
	def __init__(self, logs: Path):
		self.logs = logs

		if not self.logs.exists():
			self.logs.touch()

	def log(self, content: str):
		with open(self.logs, "a+") as f:
			now = datetime.now()
			f.write(f"[{now.strftime('%Y/%M/%d - %H:%M:%S')}] {content}\n")
	
	def read_logs(self):
		with open(self.logs, "r") as f:
			print(f.read())

	def batch_download_failed(self, id, title, reason):
		self.log("Failed to download '{title}' [batch - {id}] with reason '{reason}'")

	def download_failed(self, title, message):
		self.log("Failed to download '{title}' with the error message {message}")

	def upload_failed(self, title, reason):
		self.log("Failed to upload '{title}' with reason '{reason}'")

	def upload_succeeded(self, title, drive_folder_id):
		self.log("Uploaded '{title}' to google drive folder [{drive_folder_id}]")
	
	def batch_download_succeeded(self, id, title):
		self.log("Downloaded '{title}' [batch - {id}] successfully")
