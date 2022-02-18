import tarfile
from tempfile import TemporaryFile

from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api
from kubernetes.stream import stream

from spacecapsule.template import resource_path


def prepare_api(configfile):
    config.load_kube_config(configfile)
    try:
        c = Configuration().get_default_copy()
    except AttributeError:
        c = Configuration()
        c.assert_hostname = False
    Configuration.set_default(c)
    core_v1 = core_v1_api.CoreV1Api()
    return core_v1


def copy_tar_file_to_namespaced_pod(api_instance, namespace, name, src_path, dst_path):
    exec_command = ['tar', 'xvf', '-', '-C', '/']
    api_response = stream(api_instance.connect_get_namespaced_pod_exec, name, namespace,
                          command=exec_command,
                          stderr=True, stdin=True,
                          stdout=True, tty=False,
                          _preload_content=False)

    with TemporaryFile() as tar_buffer:
        with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
            tar.add(resource_path(src_path), dst_path)

        tar_buffer.seek(0)
        commands = [tar_buffer.read()]

        while api_response.is_open():
            api_response.update(timeout=1)
            if api_response.peek_stdout():
                print('STDOUT: {0}'.format(api_response.read_stdout()))
            if api_response.peek_stderr():
                print('STDERR: {0}'.format(api_response.read_stderr()))
            if commands:
                c = commands.pop(0)
                api_response.write_stdin(c.decode())
            else:
                break
        api_response.close()
    return True


def executor_command_inside_namespaced_pod(api_instance, namespace, name, command):
    api_response = stream(api_instance.connect_get_namespaced_pod_exec, name, namespace,
                          command=command,
                          stderr=True, stdin=False,
                          stdout=True, tty=False,
                          _preload_content=False
                          )
    stdout = api_response.readline_stdout(timeout=3)
    stderr = api_response.readline_stderr(timeout=3)
    api_response.close()
    return stdout, stderr


def check_exist_inside_namespaced_pod(api_instance, namespace, name, file_path):
    command = 'test -x {}'.format(file_path)
    executor_command_inside_namespaced_pod(api_instance, namespace, name, command)
