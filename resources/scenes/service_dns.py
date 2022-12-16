import random

import click

from resources.defects.network import dns, delay
from spacecapsule.history import check_status
from spacecapsule.k8s import prepare_api, copy_tar_file_to_namespaced_pod, \
  executor_command_inside_namespaced_pod

# case6_0:node network dns
from spacecapsule.template import resource_path


@click.command()
@click.option('--node-name', 'node_name')
@click.option('--domain', 'domain', default='www.stackoverflow.com')
@click.option('--ip', 'ip', default='10.0.0.0')
@click.option('--timeout', 'timeout', default=10000)
@click.option('--kube-config', 'kube_config', default="~/.kube/config")
def case6_0(node_name, domain, ip, timeout, kube_config):
  node_network_dns(node_name, domain, ip, timeout, kube_config)


def node_network_dns(node_name, domain, ip, timeout, kube_config):
  global api_instance, node_ip
  api_instance = prepare_api(kube_config)
  if node_name is None:
    # Choose a node
    pod_list = api_instance.list_namespaced_pod("practice")
    pod = select_pod_from_ready(pod_list.items)
    node_name = pod.spec.node_name
    print("select node_name:", node_name)
  if node_name is None:
    print("illegal node_name:", node_name)
    return

  print("node_name:", node_name, "domain:", domain, "ip:", ip)

  dns('node', domain, ip, 'case6_0', timeout, None, None, node_name,
      'Insert a network dns into node {}, domain {}, ip {}'.format(node_name,
                                                                   domain, ip))

  print("node network dns injected done！")


# case6:pod network dns
@click.command()
@click.option('--namespace', 'namespace', help="namespace")
@click.option('--pod_name', 'pod_name', help="pod-name")
@click.option('--domain', 'domain', default='www.stackoverflow.com',
              help="domain")
@click.option('--ip', 'ip', default='10.0.0.0', help="dst-ip")
@click.option('--timeout', 'timeout', default=10000)
@click.option('--kube-config', 'kube_config', default="~/.kube/config")
@click.option("--check_history", is_flag=True, default=True,
              is_eager=True, callback=check_status,
              help="Check experiment history", expose_value=False)
def case6_1(namespace, pod_name, domain, ip, timeout, kube_config):
  pod_network_dns(namespace, pod_name, domain, ip, timeout, kube_config)


def pod_network_dns(namespace, pod_name, domain, ip, timeout, kube_config):
  namespace = namespace
  pod_name = pod_name
  api_instance = prepare_api(kube_config)
  if namespace is None:
    # Choose a namespace
    namespace = "practice"
  if pod_name is None:
    # Choose a pod
    pod_list = api_instance.list_namespaced_pod(namespace)
    pod = select_pod_from_ready(pod_list.items)
    if pod is None:
      print("not find ready pod in namespace:{}", namespace)
      return
    pod_name = pod.metadata.name
    print("select namespace:" + namespace, "pod_name：", pod_name)

  print("namespace:", namespace, "pod_name:", pod_name, "domain:", domain,
        "ip:", ip)

  copy_tar_file_to_namespaced_pod(api_instance, namespace, pod_name,
                                  resource_path(
                                      './resources/chaosblade-exec/bin'),
                                  '/opt/chaosblade/bin')
  out, err = executor_command_inside_namespaced_pod(api_instance, namespace,
                                                    pod_name, [
                                                      "bash", "-c",
                                                      "chmod -R 755 /opt/chaosblade"
                                                    ])
  dns('pod', domain, ip, 'case6', timeout, None, namespace, pod_name,
      'Insert pod a network dns into namespace {} , pod {}, domain {}, ip {}'
      .format(namespace, pod_name, domain, ip))

  print("pod network dns injected done！")


@click.command()
@click.option('--namespace', 'namespace', default='kube-system')
@click.option('--network-plugin', 'network_plugin', default='calico')
@click.option('--time', 'time', default=3000)
@click.option('--offset', 'offset', default=100)
@click.option('--timeout', 'timeout')
@click.option('--kube-config', 'kube_config', default="~/.kube/config")
@click.option("--check_history", is_flag=True, default=True,
              is_eager=True, callback=check_status,
              help="Check experiment history", expose_value=False)
def case6(namespace, network_plugin, time, offset, timeout, kube_config):
  dns_pod_network_delay(namespace, network_plugin, time, offset, timeout,
                        kube_config)


def dns_pod_network_delay(namespace, network_plugin, time, offset, timeout,
    kube_config):
  # Choose a pod from target namespace
  api_instance = prepare_api(kube_config)
  pod_list = api_instance.list_namespaced_pod(namespace)

  pod = select_coredns_pod_from_ready(pod_list.items)
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
      stdout, stderr = executor_command_inside_namespaced_pod(api_instance,
                                                              'chaosblade',
                                                              pod.metadata.name,
                                                              commands)
      calico_interface = stdout
      break
  print("interface:", calico_interface, "node_name:", node_name)
  # # Choose the cali interface from target Node
  delay('node', calico_interface, time, 'case6', None, '53', None, offset,
        timeout,
        None, None, None, None, node_name,
        'Insert a network delay into pod {}, time {}, offset {}, timeout {}'.format(
            pod_name, time, offset,
            timeout))

  print("dns network delay injected done！")


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


def select_coredns_pod_from_ready(pods):
  ready = []
  for pod in pods:
    if "coredns" in pod.metadata.name:
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
