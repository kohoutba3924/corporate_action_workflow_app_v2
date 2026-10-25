# src/corporate_action_workflow_app_v2/persistence/locks.py

import errno
import os
import time

# Windows-only locking
try:
    import msvcrt

    WINDOWS = True
except ImportError:
    WINDOWS = False

# Unix-only locking
try:
    import fcntl

    UNIX = True
except ImportError:
    UNIX = False


class FileLock:
    """
    Cross-platform file lock using lock files.
    - Windows: msvcrt.locking
    - Unix: fcntl.flock
    """

    def __init__(self, lock_path: str):
        self.lock_path = lock_path
        self._fd = None

    def acquire(self, retry_interval: float = 0.05) -> None:
        """
        Acquire the lock (blocking).
        Retries until the lock is available.
        """
        while True:
            try:
                # Open or create the lock file
                self._fd = os.open(self.lock_path, os.O_RDWR | os.O_CREAT)

                if WINDOWS:
                    try:
                        msvcrt.locking(self._fd, msvcrt.LK_NBLCK, 1)
                        return
                    except OSError:
                        os.close(self._fd)
                        time.sleep(retry_interval)
                        continue

                if UNIX:
                    try:
                        fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        return
                    except OSError as e:
                        if e.errno in (errno.EACCES, errno.EAGAIN):
                            os.close(self._fd)
                            time.sleep(retry_interval)
                            continue
                        raise

                # If neither Windows nor Unix locking is available
                raise RuntimeError("File locking not supported on this platform.")

            except FileNotFoundError:
                # Rare case: directory missing
                time.sleep(retry_interval)

    def release(self) -> None:
        """
        Release the lock.
        """
        if self._fd is None:
            return

        try:
            if WINDOWS:
                msvcrt.locking(self._fd, msvcrt.LK_UNLCK, 1)

            if UNIX:
                fcntl.flock(self._fd, fcntl.LOCK_UN)

        finally:
            os.close(self._fd)
            self._fd = None
