"""Config loading. One YAML file per experiment; its hash names the run."""
import copy
import hashlib
import json

import yaml


class Cfg(dict):
    """A dict you can also read with dots: cfg.audio.sample_rate."""

    def __getattr__(self, k):
        try:
            v = self[k]
        except KeyError as e:
            raise AttributeError(k) from e
        return Cfg(v) if isinstance(v, dict) and not isinstance(v, Cfg) else v


def _merge(base, over):
    out = copy.deepcopy(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def load(path, overrides=None):
    """Load a YAML config. A file may name `inherit: other.yaml` to extend it.

    `overrides` is a list of "a.b.c=value" strings from the command line.
    """
    import os
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    parent = cfg.pop("inherit", None)
    if parent:
        cfg = _merge(load(os.path.join(os.path.dirname(path), parent)), cfg)
    for item in overrides or []:
        key, val = item.split("=", 1)
        node = cfg
        parts = key.split(".")
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = yaml.safe_load(val)
    return Cfg(cfg)


def config_hash(cfg):
    """Stable 8-character hash of the config, so every checkpoint says what made it."""
    blob = json.dumps(cfg, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()[:8]
