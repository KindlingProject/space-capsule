# case12
from spacecapsule.k8s import copy_tar_file_to_namespaced_pod, prepare_api, executor_command_inside_namespaced_pod
from spacecapsule.template import resource_path


def case12():
    print('TODO')


def slow_code(namespace, pod, claz, method, inject_code):
    print('TODO')


def runtime_err():
    print('TODO')


def dead_lock():
    print('TODO')


def inject_code(namespace, pod, process_name, pid, claz, method, code_src, kube_config):
    api_instance = prepare_api(kube_config)
    # Check chaosblade is existed or not
    copy_tar_file_to_namespaced_pod(api_instance, namespace, pod, resource_path('./resources/chaosblade'))
    # Check chaosblade is prepared or not
    print('check prepare')
    executor_command_inside_namespaced_pod()
    # Ask k8s_executor to inject target code
    # Save the UID which blade create
