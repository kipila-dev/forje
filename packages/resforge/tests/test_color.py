import pytest
from resforge.color import Color


class TestParse:
    def test_hex(self):
        assert Color.parse("#ffffff").in_srgb_gamut()

    def test_passthrough(self):
        c = Color.parse("#ff0000")
        assert Color.parse(c) is c

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Invalid value"):
            Color.parse("notacolor")


class TestSrgb:
    def test_out_of_range(self):
        with pytest.raises(ValueError, match="sRGB components"):
            Color.srgb(1.1, 0.0, 0.0)

    def test_alpha_preserved(self):
        assert Color.srgb(1.0, 0.0, 0.0, alpha=0.5).alpha == 0.5


class TestP3:
    def test_red_is_wide_gamut(self):
        assert not Color.p3(1.0, 0.0, 0.0).in_srgb_gamut()

    def test_out_of_range(self):
        with pytest.raises(ValueError, match="P3 components"):
            Color.p3(1.1, 0.0, 0.0)


class TestOklch:
    def test_negative_chroma_raises(self):
        with pytest.raises(ValueError, match="chroma"):
            Color.oklch(0.5, -0.1, 180.0)

    def test_lightness_out_of_range(self):
        with pytest.raises(ValueError, match="lightness"):
            Color.oklch(1.1, 0.0, 0.0)

    def test_wide_gamut_is_not_srgb(self):
        assert not Color.oklch(0.7, 0.35, 140.0).in_srgb_gamut()


class TestOutputs:
    def test_srgb_white(self):
        assert Color.srgb(1.0, 1.0, 1.0).to_srgb_components() == (1.0, 1.0, 1.0, 1.0)

    def test_argb_hex_white(self):
        assert Color.srgb(1.0, 1.0, 1.0).to_srgb_argb_hex() == "#FFFFFFFF"

    def test_argb_hex_prefix(self):
        assert Color.srgb(1.0, 1.0, 1.0).to_srgb_argb_hex(prefix="0x") == "0xFFFFFFFF"

    def test_wide_gamut_fits_srgb(self):
        r, g, b, _ = Color.oklch(0.7, 0.35, 140.0).to_srgb_components()
        assert 0.0 <= r <= 1.0
        assert 0.0 <= g <= 1.0
        assert 0.0 <= b <= 1.0

    def test_wide_gamut_fits_p3(self):
        r, g, b, _ = Color.oklch(0.7, 0.35, 140.0).to_p3_components()
        assert 0.0 <= r <= 1.0
        assert 0.0 <= g <= 1.0
        assert 0.0 <= b <= 1.0


class TestEquality:
    def test_same_inputs_equal(self):
        assert Color.srgb(1.0, 0.0, 0.0) == Color.srgb(1.0, 0.0, 0.0)
