import click

from resources.defects.cpu import cpu
from resources.defects.disk import diskfill
from resources.defects.network import delay, loss
from resources.scenes.service_slow import pod_network_delay
from spacecapsule.history import list_experiment, show_experiment, undo_experiment
from resources.defects.resource import resource


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

cli.add_command(resource)
cli.add_command(delay)
cli.add_command(loss)
cli.add_command(cpu)
cli.add_command(diskfill)
cli.add_command(pod_network_delay)

if __name__ == '__main__':
    cli()
