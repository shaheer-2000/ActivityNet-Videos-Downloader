from typing import List
from pathlib import Path

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import ApiRequestError, GoogleDriveFile

class DriveAPI:
	def __init__(self, settings: Path, credentials: Path, videos_dir_id: str, logger: "Logger"):
		if not credentials.exists():
			credentials.touch()

		try:
			self.gauth = GoogleAuth(settings_file=settings)
			self.drive = GoogleDrive(self.gauth)
		except Exception as e:
			print(f"Failed to initialize DriveAPI | \n{e}")

		self.videos_dir_id = videos_dir_id
		self.video_files = None
		self.logger = logger

	def get_files(self) -> List[GoogleDriveFile] | None:
		# has a generated returning the next iterator if maxResults is set, shouldn't be used
		self.video_files = self.drive.ListFile({
			"q": f"'{self.videos_dir_id}' in parents and trashed=false"
		}).GetList()

	def get_file_metadata(self, file: GoogleDriveFile):
		return { "id": file.get("id"), "filename": file.get("title"), "type": file.get("mimeType"), "version": file.get("version"), "createdAt": file.get("createdDate"), "modifiedAt": file.get("modifiedDate") }

	def list_files(self):
		if self.video_files is None:
			self.get_files()

		for file in self.video_files:
			metadata = self.get_file_metadata(file)
			print(f"id = {metadata.get('id')} | filename = {metadata.get('filename')} | type = {metadata.get('type')} | version = {metadata.get('version')} | created at = {metadata.get('createdAt')} | modified at = {metadata.get('modifiedAt')}")

	def upload_files(self, files: List[Path]) -> None:
		if self.video_files is None:
			self.get_files()

		files = list(filter(lambda f: f not in self.video_files, files))
		for file in files:
			try:
				f = self.drive.CreateFile({ "parents": [{ "id": self.videos_dir_id }]})
				f.SetContentFile(file)
				f.Upload()
				self.logger.upload_succeeded(file, self.videos_dir_id)
			except ApiRequestError as e:
				print(f"Failed to upload file [{file}]\n{e}")
				self.logger.upload_failed(file, e)


if __name__ == "__main__":
	from pathlib import Path
	from dotenv import load_dotenv
	from os import environ as env

	from logger import Logger
	
	load_dotenv(dotenv_path=Path("./.env").resolve())

	gdrive = DriveAPI(Path("./gdrive.settings.yaml").resolve(), Path("./credentials.json").resolve(), env.get("VIDEO_FOLDER_ID"))

	gdrive.list_files()
	