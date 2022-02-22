import click

from resources.scenes.jvm_inject import case14, case12, case13, case15
from resources.scenes.resource import case8, case9, case11
from resources.scenes.service_loss import case3, case4
from resources.scenes.service_slow import case2, case1
from resources.scenes_instance.cloud_instance import *
from spacecapsule.history import list_experiment, show_experiment, undo_experiment


@click.group()
def cli():
    pass


@click.command()
def history():
    list_experiment()


@click.command()
@click.argument('experiment')
def show(experiment):
    show_experiment(experiment)


@click.command()
@click.argument('experiment')
def undo(experiment):
    undo_experiment(experiment)


cli.add_command(history)
cli.add_command(show)
cli.add_command(undo)

# cli.add_command(resource)
# cli.add_command(loss)
# cli.add_command(cpu)
# cli.add_command(diskfill)
cli.add_command(case1)
cli.add_command(case2)
cli.add_command(case3)
cli.add_command(case4)
cli.add_command(case8)
cli.add_command(case9)
cli.add_command(case11)
cli.add_command(case12)
cli.add_command(case13)
cli.add_command(case14)
cli.add_command(case15)

cli.add_command(case1_vm)
cli.add_command(case3_vm)
cli.add_command(case8_vm)
cli.add_command(case13_vm)
cli.add_command(case14_vm)

if __name__ == '__main__':
    cli()
