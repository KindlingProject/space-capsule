import random

import click

from resources.defects.network import delay
from spacecapsule.k8s import prepare_api, executor_command_inside_namespaced_pod


# case1:
def node_network_delay(interface):
    print("TODO")


# case2 only calico now
@click.command()
@click.option('--namespace', 'namespace', default='practice')
@click.option('--network-plugin', 'network_plugin', default='calico')
@click.option('--time', 'time', default=3000)
@click.option('--offset', 'offset', default=100)
@click.option('--timeout', 'timeout')
@click.option('--kube-config', 'kube_config', default="~/.kube/config")
def case2(namespace, network_plugin, time, offset, timeout, kube_config):
    pod_network_delay(namespace, network_plugin, time, offset, timeout, kube_config)


def pod_network_delay(namespace, network_plugin, time, offset, timeout, kube_config):
    # Choose a pod from target namespace
    api_instance = prepare_api(kube_config)
    pod_list = api_instance.list_namespaced_pod(namespace)

    pod = select_pod_from_ready(pod_list.items)
    pod_name = pod.metadata.name
    host_ip = pod.status.host_ip
    pod_ip = pod.status.pod_ip
    node_name = pod.spec.node_name
    calico_interface = ""

    commands = [
        '/bin/sh',
        '-c',
        'ip route | grep {} '.format(pod_ip) + '| awk \'{print $3}\'',
    ]

    pod_list = api_instance.list_namespaced_pod('chaosblade')
    for pod in pod_list.items:
        if pod.status.host_ip == host_ip:
            stdout, stderr = executor_command_inside_namespaced_pod(api_instance, 'chaosblade', pod.metadata.name,
                                                                    commands)
            calico_interface = stdout
            break
    print("interface:", calico_interface, "node_name:", node_name)
    # # Choose the cali interface from target Node
    delay('node', calico_interface, time, 'case2', None, '8080', None, offset, timeout,
          None, None, None, None, node_name,
          'Insert a network delay into pod {}, time {}, offset {}, timeout {}'.format(pod_name, time, offset,
                                                                                      timeout))


def select_pod_from_ready(pods):
    ready = []
    for pod in pods:
        if pod_ready(pod):
            ready.append(pod)
    if len(ready) == 0:
        print('缺少合适的Pod')
        return None
    index = random.randint(0, len(ready) - 1)
    return ready[index]


def pod_ready(pod):
    for condition in pod.status.conditions:
        if condition.type == 'Ready' and condition.status == 'True':
            return True
    return False
