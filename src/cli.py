import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from typing import Optional

import json
from .scenario import RulesModel, ScenarioModel


@click.command()
@optgroup.group(
    "Application mode.",
    cls=RequiredMutuallyExclusiveOptionGroup,
    help="The modes of the application",
)
@optgroup.option(
    "-i", "--interactive", "interactive_mode", is_flag=True, help="interactive"
)
@optgroup.option(
    "-f",
    "--file",
    "input_file_name",
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="file",
)
def cli(interactive_mode: bool, input_file_name: Optional[str]):
    """need to add better description..."""
    if interactive_mode:
        click.echo("🧭 Interactive scenario setup")

        name = click.prompt("Scenario name", default="MyPark")
        background = click.prompt("Background (day/night)", default="day")
        max_guests = click.prompt("Max guests", type=int, default=100)
        spawn_rate = click.prompt("Spawn rate", type=float, default=1.0)

        model = ScenarioModel(
            name=name,
            background=background,
            rules=RulesModel(max_guests=max_guests, spawn_rate=spawn_rate),
            rides=[],
        )

        scenario = model.build()
        click.echo("\n✅ Scenario created successfully!")
        _print_scenario(scenario)
        return

    # ──────────────────────────────────────────────
    # Load from file
    # ──────────────────────────────────────────────
    if input_file_name:
        click.echo(f"📂 Loading scenario from file: {input_file_name}")

        with open(input_file_name, "r") as f:
            data = json.load(f)

        model = ScenarioModel.model_validate(data)
        scenario = model.build()

        click.echo("\n✅ Scenario loaded successfully!")
        _print_scenario(scenario)
        return


# ──────────────────────────────────────────────
# Helper to display a scenario nicely
# ──────────────────────────────────────────────
def _print_scenario(scenario):
    click.echo("──────────────────────────────")
    click.echo(f"🎢 Scenario: {scenario.name}")
    click.echo(f"🌅 Background: {scenario.background}")
    click.echo(f"👥 Max guests: {scenario.rules.max_guests}")
    click.echo(f"🐣 Spawn rate: {scenario.rules.spawn_rate}")
    click.echo(f"🎠 Rides ({len(scenario.rides)} total):")

    if not scenario.rides:
        click.echo("   (no rides configured)")
    else:
        for ride in scenario.rides:
            # Assuming each ride has .__class__.__name__ and .start_point
            name = ride.__class__.__name__
            pos = ride.start_point
            click.echo(f"   - {name} @ ({pos.x:.2f}, {pos.y:.2f})")

    click.echo("──────────────────────────────")
