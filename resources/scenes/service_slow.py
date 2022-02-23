import json
import random

import click
import jsonpath

from resources.defects.network import delay
from spacecapsule.k8s import prepare_api, executor_command_inside_namespaced_pod


# case1:node network delay
@click.command()
@click.option('--node-name', 'node_name')
@click.option('--interface', 'interface')
@click.option('--time', 'time', default=3000)
@click.option('--offset', 'offset', default=100)
@click.option('--timeout', 'timeout', default=10000)
@click.option('--kube-config', 'kube_config', default="~/.kube/config")
def case1(node_name, interface, time, offset, timeout, kube_config):
    node_network_delay(node_name, interface, time, offset, None, None, timeout, kube_config)


def node_network_delay(node_name, interface, time, offset, remote_port, local_port, timeout, kube_config):
    api_instance = prepare_api(kube_config)
    if node_name is None:
        # Choose a node
        pod_list = api_instance.list_namespaced_pod("practice")
        pod = select_pod_from_ready(pod_list.items, None, None)
        node_ip = pod.status.host_ip
        node_name = pod.spec.node_name
        print("select node_name:", node_name)
    else:
        node_list = api_instance.list_node()
        node_ip = select_node_ip(node_list.items, node_name)
        if node_ip is None:
            print("illegal node_name:not find node_ip", node_name)
            return

    if interface is None:
        # Choose a interface
        commands = [
            '/bin/sh',
            '-c',
            'ifconfig | grep -B 1 {}'.format(node_ip) + '| awk \'NR==1{print $1}\'',
        ]

        chaosblade_pod_list = api_instance.list_namespaced_pod('chaosblade')
        for chaosblade_pod in chaosblade_pod_list.items:
            if chaosblade_pod.spec.node_name == node_name:
                stdout, stderr = executor_command_inside_namespaced_pod(api_instance, 'chaosblade',
                                                                        chaosblade_pod.metadata.name,
                                                                        commands)
                interface = stdout
                print("select interface:", interface)
                break

    print("interface:", interface, "node_name:", node_name)
    delay('node', interface, time, 'case1', None, remote_port, local_port, offset, timeout,
          None, '22,10250', None, None, node_name, 'Insert a network delay into node {}, time {}, offset {}, timeout {}'
          .format(node_name, time, offset, timeout))

    print("node network delay injected done！")

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

    pod = select_pod_from_ready(pod_list.items, None, None)
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

    print("pod network delay injected done！")


def field_selector(pod, fields):
    return jsonpath.jsonpath(pod, fields.key) == fields.value


def select_pod_from_ready(pods, selector, selector_args):
    ready = []
    for pod in pods:
        if selector is None:
            if pod_ready(pod):
                ready.append(pod)
            else:
                continue
        elif selector(pod, selector_args):
            ready.append(pod)
        else:
            continue
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


def select_node_ip(nodes, input_node_name):
    for node in nodes:
        if input_node_name == node.metadata.name:
            for addr in node.status.addresses:
                if addr.type == 'InternalIP':
                    return addr.address
