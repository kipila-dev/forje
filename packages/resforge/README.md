# resforge

A fluent Python library for generating Android XML resource files.

Generate Android resource files programmatically instead of writing XML by hand.
Perfect for CI pipelines, design system syncing, and large-scale apps.

## Why resforge?

Writing Android XML manually doesn’t scale well when:

- Resources are generated from data (APIs, JSON, design tokens)
- You maintain multiple brands / environments
- Values need to stay consistent across files
- You want automation in CI/CD

**resforge** lets you define everything in Python and generate clean, valid XML automatically.

## Installation

```bash
pip install resforge
```

## Quick Example

```python
from resforge.android import ValuesWriter, dp, sp

with ValuesWriter("res/values/resources.xml") as res:
    res.string(
        app_name="My App",
        welcome_message="Welcome!",
    )

    res.color(
        primary="#FF6200EE",
        secondary="#FF03DAC5",
    )

    res.dimension(
        padding_small=dp(8),
        text_body=sp(16),
    )
```

### Output

```xml
<resources>
    <string name="app_name">My App</string>
    <string name="welcome_message">Welcome!</string>

    <color name="primary">#FF6200EE</color>
    <color name="secondary">#FF03DAC5</color>

    <dimen name="padding_small">8dp</dimen>
    <dimen name="text_body">16sp</dimen>
</resources>
```

## Features

- Fluent, Pythonic API
- Supports all Android `res/values/` types
- Automatic XML formatting
- Clean grouping with comments
- CI/CD friendly

## Full Example

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

## Roadmap

- iOS support (`xcassets`)

## License

MIT
