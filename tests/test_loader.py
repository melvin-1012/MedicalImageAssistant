import pytest
from cv.image_loader import ImageLoader


def test_loader_ready_and_formats():
    loader = ImageLoader()
    assert loader.ready
    assert ".png" in loader.supported_extensions


def test_load_not_implemented_yet():
    with pytest.raises(NotImplementedError):
        ImageLoader().load("x.png")
