import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from typing import Optional

import json

from src.assets.person import Person
from .scenario import RulesModel, ScenarioModel
from .engine import Engine


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
    model: ScenarioModel
    if interactive_mode:
        # TODO: interactive mode
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

    elif input_file_name:
        click.echo(f"📂 Loading scenario from file: {input_file_name}")
        with open(input_file_name, "r") as f:
            data = json.load(f)

        model = ScenarioModel.model_validate(data)

    else:
        raise click.UsageError("You must provide either --interactive or --file")

    scenario = model.build()
    click.echo("\n✅ Scenario loaded successfully!")
    print("at engine")
    engine: Engine = Engine(scenario)
    engine.run()
