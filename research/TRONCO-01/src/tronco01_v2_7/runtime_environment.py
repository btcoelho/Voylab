"""Check pinned package versions without importing ML frameworks or loading weights."""
import importlib.metadata
import platform


def inspect_runtime() -> dict:
    return {"python": platform.python_version(),
            "transformers": importlib.metadata.version("transformers"),
            "lm_format_enforcer": importlib.metadata.version("lm-format-enforcer"),
            "unsloth": importlib.metadata.version("unsloth"),
            "torch": importlib.metadata.version("torch"),
            "bitsandbytes": importlib.metadata.version("bitsandbytes")}


def verify_runtime(expected: dict) -> dict:
    actual = inspect_runtime()
    differences = {key: {"expected": value, "actual": actual.get(key)}
                   for key, value in expected.items() if actual.get(key) != value}
    if differences:
        raise RuntimeError(f"runtime differs from preregistration: {differences}")
    return actual
