import pytest

from resforge.types import Color


class TestColor:
    def test_from_hex_rgb(self):
        c = Color("#FFF")
        assert c.red == 1.0
        assert c.green == 1.0
        assert c.blue == 1.0
        assert c.alpha == 1.0

    def test_from_hex_argb(self):
        c = Color("#8FFF")
        assert c.red == 1.0
        assert c.green == 1.0
        assert c.blue == 1.0
        assert c.alpha == pytest.approx(0x88 / 255)

    def test_from_hex_rrggbb(self):
        c = Color("#FFFFFF")
        assert c.red == 1.0
        assert c.green == 1.0
        assert c.blue == 1.0
        assert c.alpha == 1.0

    def test_from_hex_aarrggbb(self):
        c = Color("#80FFFFFF")
        assert c.red == 1.0
        assert c.green == 1.0
        assert c.blue == 1.0
        assert c.alpha == pytest.approx(0x80 / 255)

    @pytest.mark.parametrize("invalid_hex", ["#FF", "#FFFFF", "#GGGGGG", "FFF"])
    def test_invalid_hex_raises(self, invalid_hex):
        with pytest.raises(ValueError, match="Invalid hex color"):
            Color(invalid_hex)

    def test_idempotent(self):
        c = Color("#FF6200EE")
        assert Color(c) is c

    def test_equality(self):
        assert Color("#FF6200EE") == Color("#FF6200EE")

    def test_hex_case_insensitive(self):
        assert Color("#abc") == Color("#ABC")

    def test_hex_round_trip(self):
        hex_str = "#12345678"
        c = Color(hex_str)
        assert c.hex == hex_str
