# case12
import json

import jsonpath

from resources.scenes.service_slow import select_pod_from_ready
from spacecapsule.executor import inject_code, delay_code
from spacecapsule.k8s import prepare_api


def case12(namespace, pod, time, offset, kube_config):
    slow_code(namespace, pod, time, offset, kube_config)


def case14(namespace, pod, kube_config):
    unexpected_err(namespace, pod, kube_config)


def case15(namespace, pod, kube_config):
    slow_sql(namespace, pod, kube_config)


def slow_code(namespace, pod, time, offset, kube_config):
    delay_code(namespace, pod, 'java', None, 'com.imooc.appoint.service.Impl.PracticeServiceImpl', 'mysqlSuccess', time,
               offset, kube_config)


def slow_sql(namespace, pod, kube_config):
    api_instance = prepare_api(kube_config)
    if pod is None:
        pod_list = api_instance.list_namespaced_pod(namespace)
        pod_info = select_pod_from_ready(pod_list.items, None, None)
    inject_code(namespace, pod_info.metadata.name, 'java', None, 'com.imooc.appoint.service.Impl.PracticeServiceImpl',
                'mysqlSuccess', '/opt/chaosblade/script/SlowSqlService.java', 'slowSql')


def unexpected_err(namespace, pod, kube_config):
    api_instance = prepare_api(kube_config)
    if pod is None:
        pod_list = api_instance.list_namespaced_pod(namespace)
        pod_info = select_pod_from_ready(pod_list.items, None, None)
    inject_code(namespace, pod_info.metadata.name, 'java', None, 'com.imooc.appoint.service.Impl.PracticeServiceImpl',
                'mysqlSuccess', '/opt/chaosblade/script/BusinessCodeService.java', 'specifyReturnOb')


def dead_lock(namespace, pod, kube_config):
    api_instance = prepare_api(kube_config)
    if pod is None:
        pod_list = api_instance.list_namespaced_pod(namespace)
        pod_info = select_pod_from_ready(pod_list.items, None, None)
    inject_code(namespace, pod_info.metadata.name, 'java', None, 'com.imooc.appoint.service.Impl.PracticeServiceImpl',
                'mysqlSuccess', '/opt/chaosblade/script/DeadLockService.java', 'Deadlock')
