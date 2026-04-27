from pathlib import Path

import pytest
from defusedxml.ElementTree import parse

from resforge.android import PluralValues, ValuesWriter, dp, inch, mm, pt, px, sp
from resforge.types import Color


class TestDimension:
    def test_str(self):
        assert str(dp(8)) == "8dp"
        assert str(sp(16)) == "16sp"

    def test_str_strips_trailing_zeros(self):
        assert str(dp(8.0)) == "8dp"
        assert str(dp(8.5)) == "8.5dp"

    def test_repr(self):
        assert repr(dp(8)) == "Dimension(value=8, unit='dp')"

    def test_mul(self):
        assert dp(8) * 2 == dp(16)

    def test_rmul(self):
        assert 2 * dp(8) == dp(16)

    def test_mul_float(self):
        assert dp(8) * 1.5 == dp(12.0)

    def test_eq(self):
        assert dp(8) == dp(8)
        assert dp(8) != sp(8)
        assert dp(8) != dp(16)

    def test_eq_non_dimension(self):
        assert dp(8) != "8dp"

    def test_all_units(self):
        assert str(dp(1)) == "1dp"
        assert str(sp(1)) == "1sp"
        assert str(px(1)) == "1px"
        assert str(pt(1)) == "1pt"
        assert str(mm(1)) == "1mm"
        assert str(inch(1)) == "1in"


@pytest.fixture
def xml_path(tmp_path) -> Path:
    return tmp_path / "res" / "values" / "test.xml"


class TestValuesWriterContextManager:
    def test_creates_file(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.string(foo="bar")
        assert xml_path.exists()

    def test_creates_parent_dirs(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.string(foo="bar")
        assert xml_path.parent.exists()

    def test_no_write_on_exception(self, xml_path: Path):
        with pytest.raises(ValueError, match="oops"), ValuesWriter(xml_path) as _:
            raise ValueError("oops")
        assert not xml_path.exists()

    def test_runtime_error_outside_context(self, xml_path: Path):
        res = ValuesWriter(xml_path)
        with pytest.raises(RuntimeError):
            res.string(foo="bar")


class TestString:
    def test_single(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.string(app_name="My App")
        root = parse(xml_path)
        elem = root.find("string[@name='app_name']")
        assert elem is not None
        assert elem.text == "My App"

    def test_multiple(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.string(foo="Foo", bar="Bar")
        root = parse(xml_path)
        foo = root.find("string[@name='foo']")
        bar = root.find("string[@name='bar']")
        assert foo is not None
        assert bar is not None
        assert foo.text == "Foo"
        assert bar.text == "Bar"

    def test_escapes_apostrophe(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.string(msg="it's here")
        root = parse(xml_path)
        elem = root.find("string[@name='msg']")
        assert elem is not None
        assert "\\'" in elem.text  # type: ignore[operator]

    def test_escapes_at_sign(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.string(msg="@hello")
        root = parse(xml_path)
        elem = root.find("string[@name='msg']")
        assert elem is not None
        assert elem.text is not None
        assert elem.text.startswith("\\")

    def test_duplicate_raises(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.string(foo="a")
            with pytest.raises(ValueError, match="Duplicate"):
                res.string(foo="b")

    def test_invalid_name_raises(self, xml_path: Path):
        with pytest.raises(ValueError, match="Invalid"), ValuesWriter(xml_path) as res:
            res.string(**{"Invalid Name": "val"})


class TestBoolean:
    def test_true(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.boolean(flag=True)
        elem = parse(xml_path).find("bool[@name='flag']")
        assert elem is not None
        assert elem.text == "true"

    def test_false(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.boolean(flag=False)
        elem = parse(xml_path).find("bool[@name='flag']")
        assert elem is not None
        assert elem.text == "false"


class TestColor:
    def test_hex_string(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.color(primary="#FF6200EE")
        elem = parse(xml_path).find("color[@name='primary']")
        assert elem is not None
        assert elem.text == "#FF6200EE"

    def test_color(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.color(primary=Color("#FF6200EE"))
        elem = parse(xml_path).find("color[@name='primary']")
        assert elem is not None
        assert elem.text == "#FF6200EE"

    def test_invalid_string_raises(self, xml_path: Path):
        with pytest.raises(ValueError, match="Invalid"), ValuesWriter(xml_path) as res:
            res.color(primary="notacolor")


class TestDimensionWriter:
    def test_dp(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.dimension(padding=dp(8))
        elem = parse(xml_path).find("dimen[@name='padding']")
        assert elem is not None
        assert elem.text == "8dp"

    def test_sp(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.dimension(text=sp(16))
        elem = parse(xml_path).find("dimen[@name='text']")
        assert elem is not None
        assert elem.text == "16sp"


class TestInteger:
    def test_value(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.integer(retries=3)
        elem = parse(xml_path).find("integer[@name='retries']")
        assert elem is not None
        assert elem.text == "3"


class TestResId:
    def test_creates_id(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.res_id("btn_ok")
        elem = parse(xml_path).find("item[@name='btn_ok']")
        assert elem is not None
        assert elem.get("type") == "id"


class TestArrays:
    def test_string_array(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.string_array("planets", ["Earth", "Mars"])
        items = parse(xml_path).findall("string-array[@name='planets']/item")
        assert [i.text for i in items] == ["Earth", "Mars"]

    def test_integer_array(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.integer_array("nums", [1, 2, 3])
        items = parse(xml_path).findall("integer-array[@name='nums']/item")
        assert [i.text for i in items] == ["1", "2", "3"]

    def test_typed_array_preserves_references(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.typed_array("icons", ["@drawable/home"])
        item = parse(xml_path).find("array[@name='icons']/item")
        assert item is not None
        assert item.text == "@drawable/home"


class TestPlurals:
    def test_quantities(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.plurals(count=PluralValues(one="%d item", other="%d items"))
        root = parse(xml_path)
        one = root.find("plurals[@name='count']/item[@quantity='one']")
        other = root.find("plurals[@name='count']/item[@quantity='other']")
        assert one is not None
        assert other is not None
        assert one.text == "%d item"
        assert other.text == "%d items"


class TestStyle:
    def test_style(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.style("AppTheme", parent="Theme.Material", colorPrimary="@color/red")
        root = parse(xml_path)
        style = root.find("style[@name='AppTheme']")
        assert style is not None
        assert style.get("parent") == "Theme.Material"
        item = style.find("item[@name='colorPrimary']")
        assert item is not None
        assert item.text == "@color/red"

    def test_style_no_parent(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.style("MyStyle")
        style = parse(xml_path).find("style[@name='MyStyle']")
        assert style is not None
        assert style.get("parent") is None


class TestComment:
    def test_comment_sanitizes_double_dash(self, xml_path: Path):
        with ValuesWriter(xml_path) as res:
            res.comment("hello -- world")
            res.string(foo="bar")
        content = xml_path.read_text()
        assert "<!-- hello - - world -->" in content
