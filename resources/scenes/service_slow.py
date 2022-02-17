import random

import click

from resources.defects.network import delay
from spacecapsule.k8s import prepare_api, executor_command_inside_namespaced_pod


# case1:
def node_network_delay(interface):
    print("TODO")


# case2 only calico now
@click.command()
@click.option('--namespace', 'namespace')
@click.option('--network-plugin', 'network_plugin')
@click.option('--time', 'time')
@click.option('--offset', 'offset')
@click.option('--timeout', 'timeout')
@click.option('--kube-config', 'kube_config', default="~/.kube/config")
def pod_network_delay(namespace, network_plugin, time,offset,timeout,kube_config):
    # Choose a pod from target namespace
    api_instance = prepare_api(kube_config)
    pod_list = api_instance.list_namespaced_pod(namespace)
    index = random.randint(0,  len(pod_list.items))
    print(index)
    print(pod_list)
    print("debug:podIp:%s;hostIp:%s".format(pod_list[index].status.pod_ip, pod_list[index].status.host_ip))
    host_ip = pod_list[index].status.host_ip
    pod_ip = pod_list[index].status.pod_ip
    node_name = pod_list[index].spec.node_name
    calico_interface = ""

    pod_list = api_instance.list_namespaced_pod('chaosblade')
    for pod in pod_list.items:
        if pod.status.host_ip == host_ip:
            calico_interface = executor_command_inside_namespaced_pod(api_instance, 'chaosblade', pod.metadata.name,"ip route | grep "+pod_ip+'  | awk \'{print $3}\'')

    print(calico_interface,node_name)
    # # Choose the cali interface from target Node
    # delay('node', calico_interface, time, 'case1', None, '8080', None, offset, timeout,
    #       None, None, None, None, node_name)

