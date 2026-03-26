from pathlib import Path

from core.models.config import Config
from storage.serializers.config_serializer import ConfigSerializer


def test_config_roundtrip(tmp_path: Path) -> None:
    serializer = ConfigSerializer()
    config = Config(name="Serializer Test", steps=[{"id": "1", "type": "click"}])
    path = tmp_path / "config.json"
    serializer.dump(config, path)
    loaded = serializer.load(path)
    assert loaded.name == "Serializer Test"
    assert loaded.steps[0]["type"] == "click"
