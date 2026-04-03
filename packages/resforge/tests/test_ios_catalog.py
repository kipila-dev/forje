import json

import pytest

from resforge.apple.catalog import AssetCatalog


def test_asset_catalog_lifecycle(tmp_path):
    catalog_name = "Assets"
    output_dir = tmp_path / "App"
    final_path = output_dir / f"{catalog_name}.xcassets"
    temp_path = output_dir / f".tmp_{catalog_name}.xcassets"

    with AssetCatalog(output_dir, catalog_name) as assets:
        assets.colorset("Primary", "#FF0000")
        assert temp_path.exists()
        assert not final_path.exists()

    assert final_path.exists()
    assert (final_path / "Contents.json").exists()
    contents_file = final_path / "Primary.colorset" / "Contents.json"
    assert (contents_file).exists()
    data = json.loads(contents_file.read_text())
    assert data["colors"][0]["color"]["components"]["red"] == "1.000"
    assert not temp_path.exists()


def test_asset_catalog_atomic_failure(tmp_path):
    catalog_name = "Assets"
    output_dir = tmp_path / "App"
    final_path = output_dir / f"{catalog_name}.xcassets"
    temp_path = output_dir / f".tmp_{catalog_name}.xcassets"

    try:
        with AssetCatalog(output_dir, catalog_name) as assets:
            assets.colorset("Primary", "#FF0000")
            assert temp_path.exists()
            raise RuntimeError()
    except RuntimeError:
        pass

    assert not final_path.exists()
    assert not temp_path.exists()


def test_asset_catalog_overwrites_existing(tmp_path):
    catalog_name = "Assets"
    output_dir = tmp_path / "App"
    final_path = output_dir / f"{catalog_name}.xcassets"

    final_path.mkdir(parents=True)
    (final_path / "old.txt").write_text("stale data")

    with AssetCatalog(output_dir, catalog_name) as assets:
        assets.colorset("Secondary", "#00FF00")

    assert final_path.exists()
    assert not (final_path / "old.txt").exists()
    assert (final_path / "Contents.json").exists()


def test_require_context_enforcement(tmp_path):
    catalog = AssetCatalog(tmp_path / "App", "Assets")

    with pytest.raises(RuntimeError):
        catalog.colorset("Error", "#000000")
