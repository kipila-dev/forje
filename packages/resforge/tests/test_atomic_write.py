import pytest

from resforge._utils import atomic_write


def test_atomic_replace_existing(tmp_path):
    target = tmp_path / "output.bin"
    target.write_bytes(b"old")
    with atomic_write(target) as f:
        f.write(b"new")
    assert target.read_bytes() == b"new"
    assert not any(tmp_path.glob("*.tmp"))


def test_creates_parent_dirs(tmp_path):
    target = tmp_path / "a" / "b" / "c" / "output.bin"
    with atomic_write(target) as f:
        f.write(b"hello")
    assert target.exists()


def test_no_corruption_on_exception(tmp_path):
    target = tmp_path / "output.bin"
    target.write_bytes(b"original")

    def _broken_write() -> None:
        with atomic_write(target) as f:
            f.write(b"new corrupted data")
            raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        _broken_write()

    assert target.read_bytes() == b"original"
    assert not any(tmp_path.glob("*.tmp"))
