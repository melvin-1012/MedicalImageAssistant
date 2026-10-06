from cv.coordinates import ResizeTransform
from cv.preprocessing import Preprocessor


def test_preprocessor_ready():
    assert Preprocessor().ready


def test_identity_transform():
    t = ResizeTransform.identity((100, 80))
    assert t.original_size == t.model_size == (100, 80)
