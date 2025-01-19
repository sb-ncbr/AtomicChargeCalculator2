from io import IOBase
import os
import shutil
import uuid


class IOLocal(IOBase):
    workdir: str = os.path.join("/", "tmp", "acc2")

    def create_tmp_dir(self, name: str = "") -> str:
        path = os.path.join(IOLocal.workdir, name, str(uuid.uuid4()))
        os.makedirs(path, exist_ok=True)

        return path

    def remove_tmp_dir(self, path: str) -> None:
        shutil.rmtree(path)

    def cp(self, path_src: str, path_dst: str) -> str:
        return shutil.copy(path_src, path_dst)
