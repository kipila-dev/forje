# resforge

A fluent Python library for generating Android XML resources and Xcode Asset
Catalogs (.xcassets).

## Installation

```bash
pip install resforge
```

## Quick Example

### Android

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

### Asset Catalog (iOS)

```python
from resforge.apple import Appearance, AppleColor, AssetCatalog
from resforge.types import Color

with AssetCatalog("iOS/App", "Assets") as ac:
    ac.colorset(
        "Background",
        "#ffffff",
        AppleColor(Color.from_hex("#000000"), appearances=[Appearance.Dark]),
    )

```

```json
{
  "info": {
    "author": "xcode",
    "version": 1
  },
  "colors": [
    {
      "idiom": "universal",
      "color": {
        "components": {
          "red": "1.000",
          "green": "1.000",
          "blue": "1.000",
          "alpha": "1.000"
        },
        "color-space": "srgb"
      }
    },
    {
      "idiom": "universal",
      "color": {
        "components": {
          "red": "0.000",
          "green": "0.000",
          "blue": "0.000",
          "alpha": "1.000"
        },
        "color-space": "srgb"
      },
      "appearances": [
        {
          "appearance": "luminosity",
          "value": "dark"
        }
      ]
    }
  ]
}
```

## Features

- Fluent, Pythonic API
- Supports all Android `res/values/` types
- Built-in validation for Asset Catalog logic

## Full Android Example

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

- Support for more Asset Catalog types (ImageSet, IconSet)

## License

MIT
