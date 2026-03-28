# resforge

A fluent Python library for generating Android XML resource files.

## Installation

```bash
pip install resforge
```

## Android

```python
from resforge.android import PluralValues, ValuesWriter, dp, sp

with ValuesWriter("res/values/resources.xml") as res:
    res.comment("Strings")
    res.string(
        app_name="My App",
        welcome_message="Welcome to My App!",
    )

    res.comment("Booleans")
    res.boolean(
        feature_enabled=True,
        dark_mode=False,
    )

    res.comment("Colors")
    res.color(
        primary="#FF6200EE",
        secondary="#FF03DAC5",
        accent=0x6200EE,
    )

    res.comment("Dimensions")
    res.dimension(
        padding_small=dp(8),
        padding_large=dp(24),
        text_body=sp(16),
        text_heading=sp(24),
    )

    res.comment("Integers")
    res.integer(
        max_retries=3,
        timeout_seconds=30,
    )

    res.comment("Resource IDs")
    res.res_id("btn_submit", "tv_title", "iv_logo")

    res.comment("String arrays")
    res.string_array("planets", ["Mercury", "Venus", "Earth", "Mars"])

    res.comment("Integer arrays")
    res.integer_array("fibonacci", [1, 1, 2, 3, 5, 8, 13])

    res.comment("Typed arrays")
    res.typed_array(
        "icons", ["@drawable/home", "@drawable/settings", "@drawable/logout"]
    )

    res.comment("Plurals")
    res.plurals(
        item_count=PluralValues(one="%d item", other="%d items"),
        file_count=PluralValues(one="%d file", other="%d files"),
    )

    res.comment("Styles")
    res.style(
        "AppTheme",
        parent="Theme.MaterialComponents.DayNight",
        colorPrimary="@color/primary",
        colorSecondary="@color/secondary",
    )
```

## iOS

Coming in v0.2.0.

## License

MIT
