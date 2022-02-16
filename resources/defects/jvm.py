from spacecapsule.k8s import check_exist_inside_namespaced_pod, copy_tar_file_to_namespaced_pod, prepare_api
from spacecapsule.template import resource_path


def prepare_jvm(namespace, pod, pid, config_file):
    api_instance = prepare_api(config_file)
    if check_chaosblade_exist(api_instance, namespace, pod):
        print("TODO")


def check_chaosblade_exist(api_instance, namespace, pod):
    if check_exist_inside_namespaced_pod(api_instance, namespace, pod, '/opt/chaosblade'):
        print('Chaosblade exist')
    else:
        copy_tar_file_to_namespaced_pod(api_instance, namespace, pod, resource_path('./chaosblade'), '/opt/chaosblades')
