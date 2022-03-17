import click

from resources.scenes.service_slow import select_pod_from_ready
from spacecapsule.executor import inject_code, delay_code
from spacecapsule.history import  check_status
from spacecapsule.k8s import prepare_api


@click.command()
@click.option('--namespace', 'namespace')
@click.option('--pod', 'pod')
@click.option('--time', 'time', default=3000)
@click.option('--offset', 'offset', default=100)
@click.option('--kube-config', 'kube_config', default="~/.kube/config")
@click.option("--check_history", is_flag=True, default=True,
              is_eager=True, callback=check_status,
              help="Check experiment history", expose_value=False)
def case12(namespace, pod, time, offset, kube_config):
    slow_code(namespace, pod, time, offset, kube_config, 'case12')

    print("slow_code injected done！")


@click.command()
@click.option('--namespace', 'namespace', default="practice")
@click.option('--pod', 'pod')
@click.option('--kube-config', 'kube_config', default="~/.kube/config")
@click.option("--check_history", is_flag=True, default=True,
              is_eager=True, callback=check_status,
              help="Check experiment history", expose_value=False)
def case13(namespace, pod, kube_config):
    dead_lock(namespace, pod, kube_config, 'case13')

    print("dead_lock injected done！")


@click.command()
@click.option('--namespace', 'namespace', default="practice")
@click.option('--pod', 'pod')
@click.option('--kube-config', 'kube_config', default="~/.kube/config")
@click.option("--check_history", is_flag=True, default=True,
              is_eager=True, callback=check_status,
              help="Check experiment history", expose_value=False)
def case14(namespace, pod, kube_config):
    unexpected_err(namespace, pod, kube_config, 'case14')

    print("unexpected_err injected done！")


@click.command()
@click.option('--namespace', 'namespace')
@click.option('--pod', 'pod')
@click.option('--kube-config', 'kube_config', default="~/.kube/config")
@click.option("--check_history", is_flag=True, default=True,
              is_eager=True, callback=check_status,
              help="Check experiment history", expose_value=False)
def case15(namespace, pod, kube_config):
    slow_sql(namespace, pod, kube_config, 'case15')

    print("slow_sql injected done！")


def slow_code(namespace, pod, time, offset, kube_config, experiment_name):
    api_instance = prepare_api(kube_config)
    if pod is None:
        pod_list = api_instance.list_namespaced_pod(namespace)
        pod = select_pod_from_ready(pod_list.items, None, None).metadata.name

    if pod.startswith('bop'):
        method = 'httpTxn2And4'
    else:
        method = 'httpTxn1'
    delay_code(namespace, pod, 'java', None, 'com.imooc.appoint.service.Impl.PracticeServiceImpl', method, time,
               offset, kube_config, experiment_name)


def slow_sql(namespace, pod, kube_config, experiment_name):
    api_instance = prepare_api(kube_config)
    if pod is None:
        pod_list = api_instance.list_namespaced_pod(namespace)
        pod = select_pod_from_ready(pod_list.items, None, None).metadata.name

    if pod.startswith('bop'):
        method = 'httpTxn2And4'
    else:
        method = 'httpTxn1'
    inject_code(namespace, pod, 'java', None, 'com.imooc.appoint.service.Impl.PracticeServiceImpl',
               method, None, '/opt/chaosblade/scripts/SlowSqlService.java', 'slowSql', experiment_name)


def unexpected_err(namespace, pod, kube_config, experiment_name):
    api_instance = prepare_api(kube_config)
    if pod is None:
        pod_list = api_instance.list_namespaced_pod(namespace)
        pod = select_pod_from_ready(pod_list.items, None, None).metadata.name

    if pod.startswith('bop'):
        method = 'httpTxn2And4'
    else:
        method = 'httpTxn1'
    inject_code(namespace, pod, 'java', None, 'com.imooc.appoint.service.Impl.PracticeServiceImpl',
                method, None, '/opt/chaosblade/scripts/BusinessCodeService.java', 'specifyReturnOb',
                experiment_name)


def dead_lock(namespace, pod, kube_config, experiment_name):
    api_instance = prepare_api(kube_config)
    if pod is None:
        pod_list = api_instance.list_namespaced_pod(namespace)
        pod = select_pod_from_ready(pod_list.items, None, None).metadata.name

    if pod.startswith('bop'):
        method = 'httpTxn2And4'
    else:
        method = 'httpTxn1'
    inject_code(namespace, pod, 'java', None, 'com.imooc.appoint.service.Impl.PracticeServiceImpl',
                method, None, '/opt/chaosblade/scripts/DeadLockService.java', 'Deadlock', experiment_name)
