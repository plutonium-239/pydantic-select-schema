"""The select schema of a pydantic model: what model_dump emits, not what validation accepts.

Usage: pydantic-select-schema dotted.module:Model

JSON Schema's `required` is a validation concept (the key must appear in the
input), so model_json_schema(mode="serialization") still leaves defaulted
fields out even though the serializer always emits them. This generator marks
every always-serialized field required.

Kept from pydantic's serialization mode, on purpose:
- Field(exclude=...) fields are absent from properties (never in output).
- Field(exclude_if=...) fields stay optional (their presence is conditional).
- computed fields are required (pydantic does this natively).

Not covered: dump-site flags (exclude_none, exclude_unset, ...) — properties
of the dump call, invisible to the model.
"""

from __future__ import annotations

import argparse
import importlib
import json

from pydantic import BaseModel
from pydantic.json_schema import GenerateJsonSchema
from pydantic_core import core_schema


class SelectSchema(GenerateJsonSchema):
    """Pass as model_json_schema(mode="serialization", schema_generator=...)."""

    def field_is_required(
        self,
        field: core_schema.ModelField | core_schema.DataclassField | core_schema.TypedDictField,
        total: bool,
    ) -> bool:
        return field.get("serialization_exclude_if") is None


def select_schema(model: type[BaseModel]) -> dict:
    return model.model_json_schema(mode="serialization", schema_generator=SelectSchema)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", help="dotted.module:ClassName")
    module_path, sep, class_name = parser.parse_args().model.rpartition(":")
    if not sep or not module_path or not class_name:
        parser.error("model must be dotted.module:ClassName")
    model = getattr(importlib.import_module(module_path), class_name)
    print(json.dumps(select_schema(model), indent=2))


if __name__ == "__main__":
    main()