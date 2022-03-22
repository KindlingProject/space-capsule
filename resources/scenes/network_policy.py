import click

from resources.defects.resource import network_policy
from spacecapsule.history import check_status

@click.command()
@click.option('--namespace', 'namespace', help="namespace")
@click.option('--deployment', 'deployment', help="deployment")
@click.option('--kube-config', 'kube_config', default="~/.kube/config")
@click.option("--check_history", is_flag=True, default=True,
              is_eager=True, callback=check_status,
              help="Check experiment history", expose_value=False)
def case5(namespace, deployment, kube_config):
    pod_network_policy(namespace, deployment, kube_config)


def pod_network_policy(namespace, deployment, kube_config):
    namespace = namespace
    deployment = deployment
    if namespace is None:
        namespace = "practice"
    print("namespace:", namespace, "deployment:", deployment)
    network_policy(namespace, 'app', deployment,'case5',
            'Insert pod a network policy into namespace {} , deployment {},'
             .format(namespace, deployment))
    print("pod network policy injected done！")
