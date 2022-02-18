import random

from kubernetes.config import kube_config

from resources.defects.cpu import cpu
from resources.defects.resource import resource
from resources.scenes.service_slow import select_pod_from_ready
from spacecapsule.k8s import prepare_api, executor_command_inside_namespaced_pod, prepare_app_api


def case9(namespace, deploy, requests, limits):
    api_instance = prepare_app_api(kube_config)
    if deploy is None:
        deploy_list = api_instance.list_namespaced_deployment('practice')
        index = random.randint(0, len(deploy_list.items) - 1)
        deploy = deploy_list.items[index].metadata.name
    resource(namespace, 'deploy', deploy, 'case9', None, limits, requests)


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
