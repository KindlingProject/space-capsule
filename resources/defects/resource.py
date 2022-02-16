import click
from spacecapsule.selector import get_resources
from spacecapsule.executor import bash_executor
from spacecapsule.template import resource_limit, kubectl_script


# # 为 test-ns 下的 testdemo1 这个deployment的testdemo1 容器设置资源限制
# # space-capsule resources {ns} {resources-kind} {resources-name} {container-name} [OPTION] {experiment-name}
# # OPTION:
# #     --container
# #     --limits
# #     --requests
# space-capsule resources test-ns deploy testdemo1 -container testdemo1 \
#   --limit cpu=100,mem=100 --requests cpu=100,mem=100 resourceLimitTest
#
# # space-capsule undo  {experiment-name}
# space-capsule undo resourcesLimitTest


@click.command()
@click.argument('namespace')
@click.argument('resource-type')
@click.argument('resource-name')
@click.argument('experiment-name')
@click.option('-c', '--container', 'container')
@click.option('-l', '--limits', 'limits')
@click.option('-r', '--requests', 'requests')
def resource(namespace, resource_type, resource_name, experiment_name, container, limits, requests):
    args = locals()
    # defects_info(args)
    bash_executor(kubectl_script, resource_limit, rollback_args, 'kubectl-rollback.sh', args)


def rollback_args(args):
    need = args['resource_type'] + '@$.metadata.annotations'
    anno = get_resources(args, need)
    version = anno[0][0]['deployment.kubernetes.io/revision']
    return {'history_version': int(version) - 1}
