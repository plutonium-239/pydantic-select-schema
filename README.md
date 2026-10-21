# pydantic-select-schema

Pydantic `BaseModel`s are very useful, and have become the unanimous choice for validation.
It allows you to access the schema via `model_json_schema()`, but only for the "insert"/"input" side, and not for the "select"/"output" side, i.e. what the validation accepts, not the validated data.

These terms are analogies to the insert/select schemas for databases, and more general input/output schemas like zod (javascript) offers as `z.input<T>` and `z.output<T>`. [^1]

[^1]: While these are typescript types, it is trivial to convert that into a JSON schema.

<details>
<summary>Comparison of input schema vs output schema</summary>

JSON schemas are hard to read. So this example uses typed python notation.

```python
class User(BaseModel):
    id: int
    email: str = ""
    nickname: str | None = None
    display: Literal['light', 'dark'] = 'dark'
```

### Input Schema (what the model itself defines)
```
id: int
email: str = ""
nickname: str | None = None
display: Literal['light', 'dark'] = 'dark'
```

### Output Schema
```
id: int
email: str
nickname: str | None
display: Literal['light', 'dark']
```

That is to say, 

```python
data_to_validate = {...} # this should follow the input schema

validated_user = User.model_validate(data_to_validate) # this follows the output schema

validated_user.email # str
validated_user.display # Literal['light', 'dark']
```

</details>

This tool gives you a way to access exactly that for pydantic `BaseModel`s.

## Installation

```sh
uv tool install git+https://github.com/plutonium-239/pydantic-select-schema
```
This installs an executable `pydantic-select-schema`

## Usage

Pass the model as `dotted.module:ClassName` like:

```sh
pydantic-select-schema src.models:User > user.schema.json
```

It outputs the select schema JSON to stdout.

> [!IMPORTANT]
> The module must be importable - run the command from your project root (or wherever `src.models` resolves from your `PYTHONPATH`).

## Behavior

| Behavior                          | Select schema                                                          |
|-----------------------------------|------------------------------------------------------------------------|
| Fields with a default             | `required` (the serializer always emits them)                          |
| `Field(exclude=True)`             | absent from `properties`                                               |
| `Field(exclude_if=...)`           | present but optional                                                   |
| `@computed_field`                 | `required`                                                             |
| `Optional[T]` fields              | keep their `null` type — present as `null`, not dropped                |
| Dump flags (`exclude_none` etc. ) | **not covered** — these are properties of the dump call, not the model |


## Local Building

```
uv sync
uv run pydantic-select-schema <module>:<Class>
uv build
```
