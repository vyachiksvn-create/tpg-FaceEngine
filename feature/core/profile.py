from __future__ import annotations

import copy
import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from loguru import logger


@dataclass
class ProfileConfig:
    name: str = "По умолчанию"
    description: str = ""
    recognition: dict[str, Any] = field(default_factory=dict)
    search: dict[str, Any] = field(default_factory=dict)
    import_: dict[str, Any] = field(default_factory=dict)
    quality: dict[str, Any] = field(default_factory=dict)
    gui: dict[str, Any] = field(default_factory=dict)
    performance: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProfileSnapshot:
    profile_name: str
    created_at: float
    checksum: str
    data: dict[str, Any]


class ProfileManager:
    def __init__(self, profiles_dir: str | Path | None = None) -> None:
        self._profiles_dir = Path(profiles_dir) if profiles_dir else Path.cwd() / "profiles"
        self._profiles_dir.mkdir(parents=True, exist_ok=True)
        self._profiles: dict[str, ProfileConfig] = {}
        self._snapshots: dict[str, list[ProfileSnapshot]] = {}
        self._active: str = "default"

    def load(self, name: str) -> ProfileConfig:
        path = self._profiles_dir / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Profile '{name}' not found at {path}")
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        profile = self._parse(raw)
        self._profiles[name] = profile
        logger.info(f"Profile loaded: {name}")
        return profile

    def save(self, profile: ProfileConfig, name: str | None = None) -> None:
        name = name or profile.name
        path = self._profiles_dir / f"{self._sanitize(name)}.yaml"
        data = self._serialize(profile)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        self._profiles[name] = profile
        logger.info(f"Profile saved: {name}")

    def list_profiles(self) -> list[str]:
        profiles = []
        for p in self._profiles_dir.glob("*.yaml"):
            profiles.append(p.stem)
        return sorted(profiles)

    def activate(self, name: str) -> ProfileConfig:
        if name not in self._profiles:
            self.load(name)
        self._active = name
        logger.info(f"Profile activated: {name}")
        return self._profiles[name]

    @property
    def active(self) -> ProfileConfig | None:
        return self._profiles.get(self._active)

    @property
    def active_name(self) -> str:
        return self._active

    def duplicate(self, source: str, target: str) -> ProfileConfig:
        profile = self._profiles.get(source) or self.load(source)
        new_profile = copy.deepcopy(profile)
        new_profile.name = target
        self.save(new_profile, target)
        return new_profile

    def export_profile(self, name: str, path: str | Path) -> None:
        profile = self._profiles.get(name) or self.load(name)
        data = {
            "version": "1.0",
            "profile": self._serialize(profile),
            "exported_at": time.time(),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Profile exported: {name} -> {path}")

    def import_profile(self, path: str | Path) -> ProfileConfig:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        profile_data = data.get("profile", data)
        profile = self._parse(profile_data)
        name = profile.name
        counter = 1
        original_name = name
        while name in self._profiles:
            name = f"{original_name}_{counter}"
            counter += 1
        self.save(profile, name)
        return profile

    def snapshot(self, name: str | None = None) -> ProfileSnapshot:
        profile_name = name or self._active
        profile = self._profiles.get(profile_name) or self.load(profile_name)
        data = self._serialize(profile)
        checksum = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        snapshot = ProfileSnapshot(
            profile_name=profile_name,
            created_at=time.time(),
            checksum=checksum,
            data=data,
        )
        self._snapshots.setdefault(profile_name, []).append(snapshot)
        return snapshot

    def rollback(self, name: str | None = None) -> ProfileConfig:
        profile_name = name or self._active
        snapshots = self._snapshots.get(profile_name, [])
        if not snapshots:
            raise RuntimeError(f"No snapshots available for profile '{profile_name}'")
        latest = sorted(snapshots, key=lambda s: s.created_at)[-1]
        profile = self._parse(latest.data)
        self.save(profile, profile_name)
        logger.info(f"Profile rolled back: {profile_name}")
        return profile

    def compare(self, name_a: str, name_b: str) -> dict[str, Any]:
        profile_a = self._profiles.get(name_a) or self.load(name_a)
        profile_b = self._profiles.get(name_b) or self.load(name_b)
        dict_a = self._serialize(profile_a)
        dict_b = self._serialize(profile_b)
        return self._diff_dicts(dict_a, dict_b)

    def _parse(self, data: dict[str, Any]) -> ProfileConfig:
        return ProfileConfig(
            name=data.get("name", "Профиль"),
            description=data.get("description", ""),
            recognition=data.get("recognition", {}),
            search=data.get("search", {}),
            import_=data.get("import", {}),
            quality=data.get("quality", {}),
            gui=data.get("gui", {}),
            performance=data.get("performance", {}),
        )

    def _serialize(self, profile: ProfileConfig) -> dict[str, Any]:
        return {
            "name": profile.name,
            "description": profile.description,
            "recognition": dict(profile.recognition),
            "search": dict(profile.search),
            "import": dict(profile.import_),
            "quality": dict(profile.quality),
            "gui": dict(profile.gui),
            "performance": dict(profile.performance),
        }

    def _sanitize(self, name: str) -> str:
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)

    def _diff_dicts(self, a: dict[str, Any], b: dict[str, Any], path: str = "") -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key in set(a) | set(b):
            current_path = f"{path}.{key}" if path else key
            if key not in a:
                result[current_path] = {"status": "added", "value": b[key]}
            elif key not in b:
                result[current_path] = {"status": "removed", "value": a[key]}
            elif isinstance(a[key], dict) and isinstance(b[key], dict):
                nested = self._diff_dicts(a[key], b[key], current_path)
                result.update(nested)
            elif a[key] != b[key]:
                result[current_path] = {"status": "changed", "from": a[key], "to": b[key]}
        return result