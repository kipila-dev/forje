from resforge.codegen.kotlin import KotlinFile, KotlinObject, KotlinProperty


def test_property_render():
    val_prop = KotlinProperty(name="primary", type_="Color", value="Color(0xFF6200EE)")
    assert val_prop.render() == "val primary: Color = Color(0xFF6200EE)"
    var_prop = KotlinProperty(
        name="primary", type_="Color", value="Color(0xFF6200EE)", mutability="var"
    )
    assert var_prop.render() == "var primary: Color = Color(0xFF6200EE)"


def test_object_empty():
    obj = KotlinObject("AppColors")
    assert obj.render() == "object AppColors"


def test_object_with_multiple_properties():
    obj = KotlinObject("AppColors")
    obj.property("primary", type_="Color", value="Color(0xFF6200EE)")
    obj.property("secondary", type_="Color", value="Color(0xFF03DAC5)")

    rendered = obj.render()
    assert rendered == (
        "object AppColors {\n"
        "    val primary: Color = Color(0xFF6200EE)\n"
        "    val secondary: Color = Color(0xFF03DAC5)\n"
        "}"
    )


def test_empty_file():
    f = KotlinFile(package="com.example")
    assert f.render() == "package com.example\n"


def test_file_with_imports():
    f = KotlinFile(package="com.example")
    f.import_("androidx.compose.ui.graphics.Color")
    f.import_("androidx.compose.ui.unit.dp")
    assert f.render() == (
        "package com.example\n"
        "\n"
        "import androidx.compose.ui.graphics.Color\n"
        "import androidx.compose.ui.unit.dp\n"
    )


def test_imports_are_sorted():
    f = KotlinFile(package="com.example")
    f.import_("z.Last")
    f.import_("a.First")
    rendered = f.render()
    assert rendered.index("a.First") < rendered.index("z.Last")


def test_duplicate_imports_are_deduplicated():
    f = KotlinFile(package="com.example")
    f.import_("androidx.compose.ui.graphics.Color")
    f.import_("androidx.compose.ui.graphics.Color")
    assert f.render().count("import androidx.compose.ui.graphics.Color") == 1


def test_file_preserves_member_order():
    colors = KotlinObject("AppColors")
    colors.property("primary", type_="Color", value="Color(0xFF6200EE)")
    dims = KotlinObject("AppDimens")
    dims.property("paddingSmall", type_="Dp", value="8.dp")

    f = KotlinFile(package="com.example")
    f.import_("androidx.compose.ui.graphics.Color")
    f.import_("androidx.compose.ui.unit.Dp")
    f.import_("androidx.compose.ui.unit.dp")
    f.member(colors)
    f.member(dims)

    assert f.render() == (
        "package com.example\n"
        "\n"
        "import androidx.compose.ui.graphics.Color\n"
        "import androidx.compose.ui.unit.Dp\n"
        "import androidx.compose.ui.unit.dp\n"
        "\n"
        "object AppColors {\n"
        "    val primary: Color = Color(0xFF6200EE)\n"
        "}\n"
        "\n"
        "object AppDimens {\n"
        "    val paddingSmall: Dp = 8.dp\n"
        "}\n"
    )


def test_top_level_property():
    prop = KotlinProperty(name="primary", type_="Color", value="Color(0xFF6200EE)")
    f = KotlinFile(package="com.example")
    f.member(prop)

    assert f.render() == (
        "package com.example\n\nval primary: Color = Color(0xFF6200EE)\n"
    )


def test_file_write(tmp_path):
    f = KotlinFile(package="com.example")
    f.import_("androidx.compose.ui.graphics.Color")
    f.member(
        KotlinObject("AppColors").property(
            "primary", type_="Color", value="Color(0xFF6200EE)"
        )
    )

    output = tmp_path / "ui" / "theme" / "Color.kt"
    f.write(output)

    assert output.exists()
    assert output.read_text() == f.render()
