from cv.quality import QualityAnalyzer
from cv.schemas import ImageQualityResult, QualityLevel


def test_quality_ready():
    assert QualityAnalyzer().ready


def test_default_quality_unknown():
    assert ImageQualityResult().level == QualityLevel.UNKNOWN
