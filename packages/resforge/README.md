# resforge

A type-safe Python DSL for generating native Android and iOS resources from
design tokens.

## Features

- Fluent, Pythonic API
- Jetpack Compose theme generation for colors and dimensions
- Supports all Android `res/values/` types
- Native Apple Asset Catalog (`.xcassets`) support
- Wide Gamut support with automatic sRGB fallbacks
- Built-in validation for resource names and color formats

## Installation

```sh
pip install resforge
```

## Quick Example

### Android (Jetpack Compose)

```python
from resforge.android import ComposeWriter

with ComposeWriter("Color.kt", "com.example.myapplication.ui.theme") as compose:
    compose.color(
        Purple80="#D0BCFF",
        PurpleGrey80="#CCC2DC",
        Pink80="#EFB8C8",
        Purple40="#6650a4",
        PurpleGrey40="#625b71",
        Pink40="#7D5260",
    )
```

```kotlin
package com.example.myapplication.ui.theme

import androidx.compose.ui.graphics.Color

val Purple80: Color = Color(0xFFD0BCFF)
val PurpleGrey80: Color = Color(0xFFCCC2DC)
val Pink80: Color = Color(0xFFEFB8C8)
val Purple40: Color = Color(0xFF6650A4)
val PurpleGrey40: Color = Color(0xFF625B71)
val Pink40: Color = Color(0xFF7D5260)
```

### Android (XML Resources)

```python
from resforge.android import ValuesWriter, dp, sp

with ValuesWriter("res/values/resources.xml") as res:
    res.string(
        app_name="My App",
        welcome_message="Welcome!",
    ).color(
        primary="#6200EE",
        secondary="#03DAC5",
    ).dimension(
        padding_small=dp(8),
        text_body=sp(16),
    )
```

```xml
<?xml version='1.0' encoding='utf-8'?>
<resources>
    <string name="app_name">My App</string>
    <string name="welcome_message">Welcome!</string>
    <color name="primary">#FF6200EE</color>
    <color name="secondary">#FF00FF00</color>
    <dimen name="padding_small">8dp</dimen>
    <dimen name="text_body">16sp</dimen>
</resources>
```

### Asset Catalog (iOS)

```python
from resforge import Color
from resforge.apple import Appearance, AppleColor, AssetCatalog

with AssetCatalog("App", "Assets") as catalog:
    catalog.colorset(
        "MyColor",
        AppleColor(Color.p3(0.0, 1.0, 0.0)),
        AppleColor("#000000", appearances=[Appearance.Dark]),
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
          "red": "0.000",
          "green": "1.000",
          "blue": "0.000",
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
          "green": "1.000",
          "blue": "0.000",
          "alpha": "1.000"
        },
        "color-space": "display-p3"
      },
      "display-gamut": "display-P3"
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

## Roadmap

- SwiftUI dimensions
- Typography
- Images (ImageSet, IconSet, `res/drawable` vectors)

## License

MIT
