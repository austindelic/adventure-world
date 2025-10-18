 (The file `/Users/AustinDe/projects/adventure-world/README.md` exists, but is empty)
# Adventure World

A tiny 2D amusement-park scene renderer using matplotlib. Entities are built from simple vector primitives and animated via frame timing.

## Run

Interactive mode:

```bash
python3 main.py --interactive
```

From a JSON file (see `examples/scenario1.json`):

```bash
python3 main.py --file examples/scenario1.json
```

Or via just:

```bash
just run
```

## Development

Tools are configured in `pyproject.toml`.

```bash
just format   # black
just lint     # ruff
just typecheck# mypy (light)
```

Project layout:

- `src/animation.py`: geometry primitives and animation container
- `src/engine.py`: render/update loop wiring entities, camera, and clock
- `src/entity.py`: base entity types and helpers
- `src/assets/*`: backgrounds and rides
- `examples/scenario1.json`: sample scenario

