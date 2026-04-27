import pytest

from resforge.android import ComposeWriter, Dimension, dp, sp


def test_object_colors(tmp_path):
    output = tmp_path / "AppColors.kt"
    with (
        ComposeWriter(output, package="com.example.theme") as compose,
        compose.object_("AppColors") as colors,
    ):
        colors.color(primary="#6200EE", secondary="#03DAC5")

    assert output.read_text() == (
        "package com.example.theme\n"
        "\n"
        "import androidx.compose.ui.graphics.Color\n"
        "\n"
        "object AppColors {\n"
        "    val primary: Color = Color(0xFF6200EE)\n"
        "    val secondary: Color = Color(0xFF03DAC5)\n"
        "}\n"
    )


def test_top_level_dimension(tmp_path):
    output = tmp_path / "Dimens.kt"
    with ComposeWriter(output, package="com.example.theme") as compose:
        compose.dimension(paddingSmall=dp(8), textBody=sp(16))

    assert output.read_text() == (
        "package com.example.theme\n"
        "\n"
        "import androidx.compose.ui.unit.Dp\n"
        "import androidx.compose.ui.unit.Sp\n"
        "import androidx.compose.ui.unit.dp\n"
        "import androidx.compose.ui.unit.sp\n"
        "\n"
        "val paddingSmall: Dp = 8.dp\n"
        "val textBody: Sp = 16.sp\n"
    )


def test_mixed_top_level_and_object(tmp_path):
    output = tmp_path / "Theme.kt"
    with ComposeWriter(output, package="com.example.theme") as compose:
        compose.dimension(border=dp(8))
        with compose.object_("AppColors") as colors:
            colors.color(primary="#FF0000", background="#FFFFFF")

    assert output.read_text() == (
        "package com.example.theme\n"
        "\n"
        "import androidx.compose.ui.graphics.Color\n"
        "import androidx.compose.ui.unit.Dp\n"
        "import androidx.compose.ui.unit.dp\n"
        "\n"
        "val border: Dp = 8.dp\n"
        "\n"
        "object AppColors {\n"
        "    val primary: Color = Color(0xFFFF0000)\n"
        "    val background: Color = Color(0xFFFFFFFF)\n"
        "}\n"
    )


def test_multiple_objects(tmp_path):
    output = tmp_path / "Theme.kt"
    with ComposeWriter(output, package="com.example.theme") as compose:
        with compose.object_("AppColors") as colors:
            colors.color(primary="#6200EE")
        with compose.object_("AppDimens") as dimens:
            dimens.dimension(padding_small=dp(8))

    rendered = output.read_text()
    assert "object AppColors" in rendered
    assert "object AppDimens" in rendered
    assert rendered.index("AppColors") < rendered.index("AppDimens")


def test_object_require_context_raises(tmp_path):
    output = tmp_path / "Color.kt"
    with ComposeWriter(output, package="com.example.theme") as compose:
        scope = compose.object_("AppColors")

    with pytest.raises(RuntimeError, match="requires an active 'with' context"):
        scope.color(primary="#6200EE")


def test_no_write_on_exception(tmp_path):
    output = tmp_path / "Color.kt"
    with (
        pytest.raises(RuntimeError),
        ComposeWriter(output, package="com.example.theme"),
    ):
        raise RuntimeError

    assert not output.exists()


def test_require_context_raises():
    compose = ComposeWriter("Color.kt", package="com.example.theme")
    with pytest.raises(RuntimeError, match="requires an active 'with' context"):
        compose.color(primary="#6200EE")


def test_creates_parent_directories(tmp_path):
    output = tmp_path / "ui" / "theme" / "Color.kt"
    with ComposeWriter(output, package="com.example.theme") as compose:
        compose.color(primary="#6200EE")

    assert output.exists()


def test_package_is_configurable(tmp_path):
    output = tmp_path / "Color.kt"
    with ComposeWriter(output, package="dev.kipila.example") as compose:
        compose.color(primary="#6200EE")

    assert "package dev.kipila.example" in output.read_text()


def test_unsupported_dimension_unit_raises(tmp_path):
    output = tmp_path / "Color.kt"

    with (
        pytest.raises(ValueError, match="Unsupported dimension type"),
        ComposeWriter(output, package="com.example.theme") as compose,
    ):
        compose.dimension(padding=Dimension(8, "px"))
