import random

import click
from kubernetes.config import kube_config

from resources.defects.cpu import cpu
from resources.defects.resource import resource, namespace_quota
from resources.scenes.service_slow import select_pod_from_ready
from spacecapsule.history import check_status
from spacecapsule.k8s import prepare_api, executor_command_inside_namespaced_pod, prepare_app_api


@click.command()
@click.option('--namespace', 'namespace', default='practice')
@click.option('--deploy', 'deploy')
@click.option('--requests', 'requests', default='cpu=100m,memory=400Mi')
@click.option('--limits', 'limits', default='cpu=100m,memory=400Mi')
@click.option("--check_history", is_flag=True, default=True,
              is_eager=True, callback=check_status,
              help="Check experiment history", expose_value=False)
def case9(namespace, deploy, requests, limits):
    api_instance = prepare_app_api(kube_config)
    if deploy is None:
        deploy_list = api_instance.list_namespaced_deployment('practice')
        index = random.randint(0, len(deploy_list.items) - 1)
        deploy = deploy_list.items[index].metadata.name
    resource(namespace, 'deploy', deploy, 'case9', None, limits, requests,'requests {} limits {}'
             .format(requests, limits))
    print("resource limits injected done!")

@click.command()
@click.option('--namespace', 'namespace', default='practice')
@click.option('--cpu_requests', 'cpu_requests', default='100m')
@click.option('--cpu_limits', 'cpu_limits', default='100m')
@click.option('--mem_requests', 'mem_requests', default='500Mi')
@click.option('--mem_limits', 'mem_limits', default='500Mi')
@click.option("--check_history", is_flag=True, default=True,
              is_eager=True, callback=check_status,
              help="Check experiment history", expose_value=False)
def case11(namespace, cpu_limits, mem_limits, cpu_requests, mem_requests):
    namespace_quota(namespace, cpu_limits, cpu_requests, mem_requests, mem_limits, 'case11')

    print("namespace_quota injected done！")

@click.command()
@click.option('--timeout', 'timeout')
@click.option('--names', 'names')
@click.option('--labels', 'labels')
@click.option("--check_history", is_flag=True, default=True,
              is_eager=True, callback=check_status,
              help="Check experiment history", expose_value=False)
def case8(timeout, names, labels):
    api_instance = prepare_api(kube_config)
    if names is None:
        # Choose a node
        pod_list = api_instance.list_namespaced_pod("practice")
        pod = select_pod_from_ready(pod_list.items, None, None)
        names = pod.spec.node_name
    commands = [
        '/bin/sh',
        '-c',
        'cat /proc/cpuinfo |grep processor |wc -l',
    ]
    pod_list = api_instance.list_namespaced_pod('chaosblade')
    for pod in pod_list.items:
        if pod.spec.node_name == names:
            stdout, stderr = executor_command_inside_namespaced_pod(api_instance, 'chaosblade', pod.metadata.name,
                                                                    commands)
            cpu_count = stdout
            break
    cpu('node', cpu_count, 90, 'case8', timeout, labels, None, names, None)

    print("cpu load injected done!")
