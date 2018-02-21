"""Tests to check if one image is a cropped part of another."""
import pytest
from main import subimage


@pytest.mark.parametrize(
    "image1, image2, is_crop", [
    ("1.jpeg", "2.jpeg", False),
    ("full.png", "crop.png", True),
    ("crop.png", "full.png", True),
    ("full.png", "crop_bigger.png", True),
    ("full.png", "crop_smaller.png", True),
    ("full_compression.jpg", "crop.png", True),
    ("full_compression.jpg", "1.jpeg", False),

])
def test_crops(image1, image2, is_crop):
    """Test that checks if one image is a crop from the other image."""
    crop = subimage('images/' + image1, 'images/' + image2)
    if is_crop:
        assert crop is not None
    else:
        assert crop is None
