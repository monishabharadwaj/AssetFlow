from __future__ import annotations

from typing import Any


def to_json_native(value: Any) -> Any:
    """Convert numpy/pandas scalars to JSON-serializable Python types."""
    if value is None:
        return None

    type_name = type(value).__module__
    if type_name == "numpy" or type_name.startswith("numpy."):
        import numpy as np

        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, np.ndarray):
            return value.tolist()

    if isinstance(value, dict):
        return {str(k): to_json_native(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json_native(v) for v in value]

    return value


def sanitize_feature_dict(features: dict[str, Any]) -> dict[str, Any]:
    return {key: to_json_native(features[key]) for key in features}
