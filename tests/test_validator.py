from cv.validator import ImageValidator


def test_validator_ready():
    assert ImageValidator().ready
