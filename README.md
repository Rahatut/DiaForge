# DiaForge

Declarative SVG diagram generation engine with a custom `.dia` language.

## Features

- Nodes and relationships
- Rounded cards and custom styling
- Icons
- Straight, curved, and orthogonal arrows
- Rounded corners
- Dashed edges and labels
- Rotation
- Automatic layout
- SVG output

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Windows:

```powershell
.venv\Scripts\activate
pip install -e .
```

## Render

```bash
diaforge examples/visual_test.dia -o visual_test.svg
```

Or:

```bash
python -m diaforge.cli examples/visual_test.dia -o visual_test.svg
```

Open:

```bash
xdg-open visual_test.svg
```

## Test

```bash
python -m pytest -v
```

## Structure

```text
DiaForge/
├── diaforge/
│   ├── ast.py
│   ├── lexer.py
│   ├── parser.py
│   ├── layout.py
│   ├── routing.py
│   ├── icons.py
│   ├── render_svg.py
│   └── cli.py
├── examples/
├── tests/
├── pyproject.toml
└── README.md
```

## Pipeline

```text
.dia → Lexer → Parser → AST → Layout → Routing → SVG
```

## Quick Example

```
diagram "Example" {

  node input {
    title: "Input"
    icon: "database"
    x: 100
    y: 300
  }

  node output {
    title: "Output"
    icon: "chart"
    x: 700
    y: 300
  }

  edge input -> output {
    route: curve
    curve: 50
    label: "process"
  }
}
```
