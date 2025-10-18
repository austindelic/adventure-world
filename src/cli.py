"""Command-line interface for Adventure World.

Provides two modes:
- Interactive: prompt-driven scenario creation
- File-based: load a scenario from a JSON file

Note: This module intentionally performs no heavy work at import time.
"""

from __future__ import annotations

import json
from typing import Optional

import click
from click_option_group import RequiredMutuallyExclusiveOptionGroup, optgroup

from src.engine import Engine
from src.scenario import RulesModel, ScenarioModel


@click.command()
@optgroup.group(
    "Application mode.",
    cls=RequiredMutuallyExclusiveOptionGroup,
    help="The modes of the application",
)
@optgroup.option(
    "-i",
    "--interactive",
    "interactive_mode",
    is_flag=True,
    help="Run in interactive mode and build a scenario by answering prompts",
)
@optgroup.option(
    "-f",
    "--file",
    "input_file_name",
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Path to a scenario JSON file",
)
def cli(interactive_mode: bool, input_file_name: Optional[str]):
    """Entry point for the CLI.

    Exactly one of --interactive or --file must be provided.
    """
    model: ScenarioModel
    if interactive_mode:
        # Interactive prompts to build a minimal scenario model
        click.echo("🧭 Interactive scenario setup")

        name = click.prompt("Scenario name", default="MyPark")
        background = click.prompt("Background (Day/Night)", default="Day")
        max_guests = click.prompt("Max guests", type=int, default=100)
        spawn_rate = click.prompt("Spawn rate (guests/sec)", type=float, default=1.0)
        target_fps = click.prompt("Target FPS", type=int, default=24)

        model = ScenarioModel(
            name=name,
            background=background,
            rules=RulesModel(
                max_guests=max_guests,
                spawn_rate=spawn_rate,
                target_fps=target_fps,
            ),
            rides=[],
        )

    elif input_file_name:
        click.echo(f"📂 Loading scenario from file: {input_file_name}")
        with open(input_file_name, "r", encoding="utf-8") as f:
            data = json.load(f)
        model = ScenarioModel.model_validate(data)

    else:
        raise click.UsageError("You must provide either --interactive or --file")

    scenario = model.build()
    click.echo("\n✅ Scenario loaded successfully!")
    engine: Engine = Engine(scenario)
    engine.run()
