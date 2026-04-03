import pytest

from resforge.types import Color


class TestColor:
    def test_from_components(self):
        c = Color(red=0.5, green=0.5, blue=0.5)
        assert c.red == 0.5 and c.green == 0.5 and c.blue == 0.5
        assert c.alpha == 1.0

    def test_component_out_of_range_raises(self):
        with pytest.raises(ValueError, match="between 0 and 1"):
            Color(red=1.1, green=-1.1, blue=2.0)

    def test_from_hex_rgb(self):
        c = Color.from_hex("#FFF")
        assert c.red == 1.0 and c.green == 1.0 and c.blue == 1.0
        assert c.alpha == 1.0

    def test_from_hex_argb(self):
        c = Color.from_hex("#8FFF")
        assert c.red == 1.0 and c.green == 1.0 and c.blue == 1.0
        assert c.alpha == pytest.approx(0x88 / 255)

    def test_from_hex_rrggbb(self):
        c = Color.from_hex("#FFFFFF")
        assert c.red == 1.0 and c.green == 1.0 and c.blue == 1.0
        assert c.alpha == 1.0

    def test_from_hex_aarrggbb(self):
        c = Color.from_hex("#80FFFFFF")
        assert c.red == 1.0 and c.green == 1.0 and c.blue == 1.0
        assert c.alpha == pytest.approx(0x80 / 255)

    @pytest.mark.parametrize("invalid_hex", ["#FF", "#FFFFF", "#GGGGGG", "FFF"])
    def test_from_hex_invalid_raises(self, invalid_hex):
        with pytest.raises(ValueError, match="Invalid hex color"):
            Color.from_hex(invalid_hex)

    def test_equality(self):
        assert Color(0.1, 0.2, 0.3) == Color(0.1, 0.2, 0.3)

    def test_hex_case_insensitive(self):
        assert Color.from_hex("#abc") == Color.from_hex("#ABC")

    def test_to_hex(self):
        c = Color(red=1.0, green=0.0, blue=0.0)
        assert c.to_hex == "#FFFF0000"

    def test_to_hex_zero_padding(self):
        c = Color(red=0.0, green=0.0, blue=0.0, alpha=0.0)
        assert c.to_hex == "#00000000"

    def test_to_hex_round_trip(self):
        hex_str = "#12345678"
        c = Color.from_hex(hex_str)
        assert c.to_hex == hex_str
