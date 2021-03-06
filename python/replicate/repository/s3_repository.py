from typing import AnyStr, List

from .repository_base import Repository
from .. import shared
from ..exceptions import DoesNotExistError


class S3Repository(Repository):
    """
    Stores data on Amazon S3
    """

    def __init__(self, bucket: str, root: str):
        self.bucket_name = bucket
        self.root = root

    def root_url(self):
        """
        Returns the URL this repository is pointing at
        """
        ret = "s3://" + self.bucket_name
        if self.root:
            ret += "/" + self.root
        return ret

    def get(self, path: str) -> bytes:
        """
        Get data at path
        """
        try:
            result = shared.call(
                "S3Repository.Get",
                Bucket=self.bucket_name,
                Root=self.root,
                Path=str(path),  # typecast for pathlib
            )
        except shared.SharedError as e:
            if e.type == "DoesNotExistError":
                raise DoesNotExistError(e.message)
            raise
        return result["Data"]

    def put_path(self, source_path: str, dest_path: str):
        """
        Save directory to path
        """
        shared.call(
            "S3Repository.PutPath",
            Bucket=self.bucket_name,
            Root=self.root,
            Src=str(source_path),
            Dest=str(dest_path),
        )

    def put_path_tar(self, local_path: str, tar_path: str, include_path: str):
        """
        Save file or directory to tarball
        """
        shared.call(
            "S3Repository.PutPathTar",
            Bucket=self.bucket_name,
            Root=self.root,
            LocalPath=str(local_path),
            TarPath=str(tar_path),
            IncludePath=str(include_path),
        )

    def put(self, path: str, data: AnyStr):
        """
        Save data to file at path
        """
        if isinstance(data, str):
            data_bytes = data.encode("utf-8")
        else:
            data_bytes = data
        shared.call(
            "S3Repository.Put",
            Bucket=self.bucket_name,
            Root=self.root,
            Path=str(path),
            Data=data_bytes,
        )

    def list(self, path: str) -> List[str]:
        """
        Returns a list of files at path, but not any subdirectories.
        """
        result = shared.call(
            "S3Repository.List",
            Bucket=self.bucket_name,
            Root=self.root,
            Path=str(path),  # typecast for pathlib
        )
        return result["Paths"]

    def exists(self, path: str) -> bool:
        pass

    def delete(self, path: str):
        """
        Recursively delete path
        """
        shared.call(
            "S3Repository.Delete",
            Bucket=self.bucket_name,
            Root=self.root,
            Path=str(path),  # typecast for pathlib
        )

    def get_path_tar(self, tar_path: str, local_path: str):
        """
        Extracts tarball from tar_path to local_path.
        The first component of the tarball is stripped. E.g.
        extracting a tarball with `abc123/weights` in it to
        `/code` would create `/code/weights`.
        """
        try:
            shared.call(
                "S3Repository.GetPathTar",
                Bucket=self.bucket_name,
                Root=self.root,
                TarPath=str(tar_path),
                LocalPath=str(local_path),
            )
        except shared.SharedError as e:
            if e.type == "DoesNotExistError":
                raise DoesNotExistError(e.message)
            raise
