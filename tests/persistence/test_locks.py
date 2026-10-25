# tests/persistence/test_locks.py

from unittest.mock import patch

import pytest

from corporate_action_workflow_app_v2.persistence.locks import FileLock

# =========================================================
# Construction Tests
# =========================================================


class TestFileLockConstruction:

    def test_construct_file_lock(self):
        lock = FileLock("test.lock")

        assert lock.lock_path == "test.lock"
        assert lock._fd is None


# =========================================================
# Lifecycle Tests
# =========================================================


class TestFileLockLifecycle:

    def test_acquire_and_release(self, tmp_path):
        lock_path = tmp_path / "test.lock"
        lock = FileLock(str(lock_path))

        lock.acquire()

        assert lock._fd is not None

        lock.release()

        assert lock._fd is None

    def test_lock_file_created(self, tmp_path):
        lock_path = tmp_path / "test.lock"
        lock = FileLock(str(lock_path))

        lock.acquire()

        assert lock_path.exists()

        lock.release()

    def test_reacquire_after_release(self, tmp_path):
        lock_path = tmp_path / "test.lock"
        lock = FileLock(str(lock_path))

        lock.acquire()
        first_fd = lock._fd

        lock.release()

        assert lock._fd is None

        lock.acquire()

        assert lock._fd is not None

        lock.release()

    def test_double_release_safe(self, tmp_path):
        lock_path = tmp_path / "test.lock"
        lock = FileLock(str(lock_path))

        lock.acquire()
        lock.release()

        # Explicitly exercise the guard clause
        lock.release()

        assert lock._fd is None


# =========================================================
# Platform Handling Tests
# =========================================================


class TestPlatformHandling:

    def test_unsupported_platform_raises_runtime_error(self, tmp_path):
        lock_path = tmp_path / "unsupported.lock"

        with (
            patch(
                "corporate_action_workflow_app_v2.persistence.locks.WINDOWS",
                False,
            ),
            patch(
                "corporate_action_workflow_app_v2.persistence.locks.UNIX",
                False,
            ),
        ):
            lock = FileLock(str(lock_path))

            with pytest.raises(RuntimeError):
                lock.acquire()


# =========================================================
# Retry Logic Tests
# =========================================================


class TestRetryBehavior:

    def test_windows_retry_then_success(self, tmp_path):
        """
        Verify retry behavior without real lock contention.

        This test only runs on Windows-capable environments.
        """
        lock_path = tmp_path / "retry.lock"

        call_count = {"count": 0}

        def fake_locking(fd, mode, size):
            call_count["count"] += 1

            if call_count["count"] == 1:
                raise OSError("locked")

        with (
            patch(
                "corporate_action_workflow_app_v2.persistence.locks.WINDOWS",
                True,
            ),
            patch(
                "corporate_action_workflow_app_v2.persistence.locks.UNIX",
                False,
            ),
            patch(
                "corporate_action_workflow_app_v2.persistence.locks.msvcrt.locking",
                side_effect=fake_locking,
            ),
            patch("corporate_action_workflow_app_v2.persistence.locks.time.sleep"),
        ):
            lock = FileLock(str(lock_path))

            lock.acquire()

            assert call_count["count"] >= 2

            lock.release()
