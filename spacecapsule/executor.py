import json

import jsonpath

from spacecapsule.history import store_experiment, defects_info, rollback_command
from subprocess import Popen, PIPE

from spacecapsule.k8s import prepare_api, copy_tar_file_to_namespaced_pod, executor_command_inside_namespaced_pod
from spacecapsule.template import chaosblade_prepare_script, resource_path, chaosblade_inject, chaosblade_prepare, \
    chaosblade_jvm_delay


def bash_executor(create_script, create_template, create_rollback_args, rollback_template_file, args):
    # TODO 部分参数需要executor选择
    script = create_script(create_template, args)
    process = Popen(script, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    out, err = process.communicate()

    args.update(create_rollback_args(args))
    store_experiment(args, rollback_command(rollback_template_file, args), out.decode(), err.decode())


def inject_code(namespace, pod, process_name, pid, classname, methodname, kube_config, script_file, script_name):
    args = locals()
    agent_uid, api_instance, stderr = chaosblade_jvm_prepare(args, kube_config, namespace, pod)
    # Ask k8s_executor to inject target code
    inject_command = chaosblade_prepare_script(chaosblade_inject(args))
    inject_msg, stderr = executor_command_inside_namespaced_pod(api_instance, namespace, pod, inject_command)
    experiment_uid = jsonpath.jsonpath(json.loads(inject_msg), '.results')
    # Save the UID which blade create
    args.update(agent_uid=agent_uid, experiment_uid=experiment_uid)
    store_experiment(args, rollback_command('chaosbladeJvm-rollback.sh', args), inject_msg, stderr)


def delay_code(namespace, pod, process, pid, classname, methodname, time, offset, kube_config):
    args = locals()
    agent_uid, api_instance, stderr = chaosblade_jvm_prepare(args, kube_config, namespace, pod)

    delay_command = chaosblade_prepare_script(chaosblade_jvm_delay(args))
    delay_msg, delay_err = executor_command_inside_namespaced_pod(api_instance, namespace, pod, delay_command)
    experiment_uid = jsonpath.jsonpath(json.loads(delay_msg), '.results')
    # Save the UID which blade create
    args.update(agent_uid=agent_uid, experiment_uid=experiment_uid)
    store_experiment(args, rollback_command('chaosbladeJvm-rollback.sh', args), delay_msg, stderr)


def chaosblade_jvm_prepare(args, kube_config, namespace, pod):
    api_instance = prepare_api(kube_config)
    check_result ,_ = check_chaosblade_exists(api_instance,namespace,pod)
    if check_result:
        copy_tar_file_to_namespaced_pod(api_instance, namespace, pod, resource_path('./resources/chaosblade'),
                                        '/opt/chaosblade')
    prepare_command = chaosblade_prepare_script(chaosblade_prepare(args))
    prepare_msg, stderr = executor_command_inside_namespaced_pod(api_instance, namespace, pod, prepare_command)
    agent_uid = jsonpath.jsonpath(json.loads(prepare_msg), '.results')
    return agent_uid, api_instance, stderr


def check_chaosblade_exists(api_instance, namespace, pod):
    commands = ["bash",
                "-c",
                "[ -d /opt/chaosblade ] && echo True || echo False"]
    check_msg, check_err = executor_command_inside_namespaced_pod(api_instance, namespace, pod, commands)
    return check_msg, check_err
