"""Stable pre-Framework bootstrap used by mise/tasks/setup.sh."""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def _is_reparse_point(info: os.stat_result) -> bool:
    reparse_attribute = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(getattr(info, "st_file_attributes", 0) & reparse_attribute)


def _regular_file(path: Path, *, optional: bool = False) -> os.stat_result | None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        if optional:
            return None
        raise RuntimeError(f"Required path is missing: {path}")
    if stat.S_ISLNK(info.st_mode) or _is_reparse_point(info) or not stat.S_ISREG(info.st_mode):
        raise RuntimeError(f"Refusing non-regular or linked setup path: {path}")
    return info


def _real_directory(path: Path) -> os.stat_result:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or _is_reparse_point(info) or not stat.S_ISDIR(info.st_mode):
        raise RuntimeError(f"Refusing non-directory or linked setup path: {path}")
    return info


@contextmanager
def _exclusive_setup_lock(path: Path) -> Iterator[None]:
    """Hold a cross-platform OS file lock for the entire setup transaction."""

    prior = _regular_file(path, optional=True)
    flags = os.O_CREAT | os.O_RDWR
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    if nofollow:
        flags |= nofollow
    if prior is None:
        flags |= os.O_EXCL
    descriptor = os.open(path, flags, 0o600)
    try:
        opened = os.fstat(descriptor)
        after = _regular_file(path)
        if (
            after is None
            or not stat.S_ISREG(opened.st_mode)
            or (opened.st_dev, opened.st_ino) != (after.st_dev, after.st_ino)
        ):
            raise RuntimeError(f"Setup lock changed while being opened: {path}")
        if os.name == "nt":
            import msvcrt

            if opened.st_size == 0:
                os.write(descriptor, b"\0")
                os.fsync(descriptor)
            os.lseek(descriptor, 0, os.SEEK_SET)
            try:
                msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise RuntimeError("Another `mise run setup` is already running for this Storage.") from exc
        else:
            import fcntl

            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise RuntimeError("Another `mise run setup` is already running for this Storage.") from exc
        try:
            yield
        finally:
            if os.name == "nt":
                import msvcrt

                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(descriptor, fcntl.LOCK_UN)
    finally:
        os.close(descriptor)


def _create_or_keep_marker(path: Path) -> tuple[int, int]:
    existing = _regular_file(path, optional=True)
    if existing is not None:
        return existing.st_dev, existing.st_ino

    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    if nofollow:
        flags |= nofollow
    descriptor = os.open(path, flags, 0o600)
    try:
        os.write(descriptor, f"setup pid={os.getpid()}\n".encode("ascii"))
        os.fsync(descriptor)
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode):
            raise RuntimeError(f"Setup marker is not a regular file: {path}")
        return info.st_dev, info.st_ino
    finally:
        os.close(descriptor)


def _remove_marker(path: Path, identity: tuple[int, int]) -> None:
    info = _regular_file(path)
    if info is None or (info.st_dev, info.st_ino) != identity:
        raise RuntimeError(f"Setup marker changed during setup; leaving it in place: {path}")
    path.unlink()


def _run_setup(root: Path, uv: str, marker_identity: tuple[int, int]) -> int:
    project = root / ".pkm"
    environment = os.environ.copy()
    environment["UV_PROJECT_ENVIRONMENT"] = str(project / "runtime")
    commands = (
        [uv, "sync", "--locked", "--project", str(project)],
        [uv, "run", "--locked", "--project", str(project), "pkm", "storage", "install", "--storage", str(root)],
        [uv, "run", "--locked", "--project", str(project), "pkm", "skills", "install", "--target", str(root / ".agents/skills")],
    )
    for command in commands:
        result = subprocess.run(command, cwd=root, env=environment, check=False)
        if result.returncode:
            return result.returncode
    _remove_marker(root / ".pkm/setup-incomplete", marker_identity)
    print("Storage setup complete. Framework-managed files match the pinned Framework.")
    return 0


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: setup_bootstrap.py <storage-root>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).expanduser().absolute()
    try:
        root_info = _real_directory(root)
        pkm = root / ".pkm"
        _real_directory(pkm)
        lock_path = pkm / "setup.lock"
        marker_path = pkm / "setup-incomplete"
        _regular_file(marker_path, optional=True)
        uv = shutil.which("uv")
        if uv is None:
            raise RuntimeError("uv is not on PATH; install uv and retry `mise run setup`.")
        with _exclusive_setup_lock(lock_path):
            # Re-check the Storage roots after taking the inter-process lock.
            locked_root = _real_directory(root)
            locked_pkm = _real_directory(pkm)
            if (root_info.st_dev, root_info.st_ino) != (locked_root.st_dev, locked_root.st_ino):
                raise RuntimeError("Storage root changed while setup was starting.")
            if (locked_pkm.st_dev, locked_pkm.st_ino) != (pkm.lstat().st_dev, pkm.lstat().st_ino):
                raise RuntimeError("Storage .pkm directory changed while setup was starting.")
            marker_identity = _create_or_keep_marker(marker_path)
            return _run_setup(root, uv, marker_identity)
    except (OSError, RuntimeError) as exc:
        print(f"setup: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
