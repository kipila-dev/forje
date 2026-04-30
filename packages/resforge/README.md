# resforge

A type-safe Python DSL for generating native Android and iOS resources from design tokens.

## Features

- Fluent, Pythonic API
- Jetpack Compose theme generation with type-safe color and dimension properties
- Supports all Android `res/values/` types
- Native Apple Asset Catalog (`.xcassets`) with dark mode support
- Built-in validation for resource names and color formats

## Installation

```bash
pip install resforge
```

## Quick Example

### Android (Jetpack Compose)

```python
from resforge.android import ComposeWriter, dp

with ComposeWriter("Theme.kt", "dev.kipila.example") as compose:
    compose.dimension(border=dp(8))
    with compose.object_("AppColors") as colors:
        colors.color(primary="#FF0000", background="#FFFFFF")
```

```kotlin
package dev.kipila.example

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

val border: Dp = 8.dp

object AppColors {
    val primary: Color = Color(0xFFFF0000)
    val background: Color = Color(0xFFFFFFFF)
}
```

### Android (XML Resources)

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

with AssetCatalog("App", "Assets") as ac:
    ac.colorset(
        "Background",
        "#ffffff",
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

## Roadmap

- Asset Catalog image support (ImageSet, IconSet)
- Android `res/drawable` vector asset support

## License

MIT
