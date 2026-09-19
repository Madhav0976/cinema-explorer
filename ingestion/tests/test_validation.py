import pytest
from pydantic import ValidationError
from ingestion.models.payloads import (
    IndustryClassificationPayload,
    NormalizedTitlePayload,
)


def test_validation_rejects_empty_title():
    with pytest.raises(ValidationError):
        NormalizedTitlePayload(
            tmdb_id=100,
            type="movie",
            title="   ",  # Invalid empty title
        )


def test_validation_rejects_invalid_type():
    with pytest.raises(ValidationError):
        NormalizedTitlePayload(
            tmdb_id=100,
            type="anime",  # Anime is NOT a valid content type!
            title="Valid Title",
        )


def test_validation_rejects_negative_vote_count():
    with pytest.raises(ValidationError):
        NormalizedTitlePayload(
            tmdb_id=100,
            type="movie",
            title="Valid Title",
            tmdb_vote_count=-5,
        )


def test_validation_rejects_out_of_bounds_confidence():
    with pytest.raises(ValidationError):
        IndustryClassificationPayload(
            industry_name="Tollywood",
            confidence=1.5,  # Must be between 0.0 and 1.0
            source="test",
        )

