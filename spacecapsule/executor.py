import json

import jsonpath
import paramiko

from spacecapsule.history import store_experiment, defects_info, rollback_command
from subprocess import Popen, PIPE

from spacecapsule.k8s import prepare_api, copy_tar_file_to_namespaced_pod, executor_command_inside_namespaced_pod
from spacecapsule.template import chaosblade_prepare_script, resource_path, chaosblade_inject, chaosblade_prepare, \
    chaosblade_jvm_delay, chaosblade_prepare_script_vm


def bash_executor(create_script, create_template, create_rollback_args, rollback_template_file, args):
    # TODO 部分参数需要executor选择
    script = create_script(create_template, args)
    print(script)
    process = Popen(script, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = process.communicate()
    args.update(create_rollback_args(args))
    store_experiment(args, rollback_command(rollback_template_file, args), out.decode(), err.decode())


def inject_code(namespace, pod, process_name, pid, classname, methodname, kube_config, script_file, script_name,
                experiment_name):
    args = locals()
    agent_uid, api_instance, stderr = chaosblade_jvm_prepare(args, kube_config, namespace, pod)
    print("Prepare finished, start to inject!")
    # Ask k8s_executor to inject target code
    inject_command = chaosblade_prepare_script(chaosblade_inject, args)
    inject_msg, stderr = executor_command_inside_namespaced_pod(api_instance, namespace, pod, inject_command)
    if stderr is not None:
        print(stderr)
    experiment_uid = jsonpath.jsonpath(json.loads(inject_msg), 'result')
    print('exe', experiment_uid)
    print('agent', agent_uid)
    # Save the UID which blade create
    args.update(agent_uid=agent_uid[0], experiment_uid=experiment_uid[0])
    args.update(desc=args)
    store_experiment(args, rollback_command('chaosbladeJvm-rollback.sh', args), inject_msg, stderr)


def delay_code(namespace, pod, process, pid, classname, methodname, time, offset, kube_config, experiment_name):
    args = locals()
    agent_uid, api_instance, stderr = chaosblade_jvm_prepare(args, kube_config, namespace, pod)

    delay_command = chaosblade_prepare_script(chaosblade_jvm_delay,args)
    delay_msg, delay_err = executor_command_inside_namespaced_pod(api_instance, namespace, pod, delay_command)
    experiment_uid = jsonpath.jsonpath(json.loads(delay_msg), 'result')
    # Save the UID which blade create
    args.update(agent_uid=agent_uid[0], experiment_uid=experiment_uid[0])
    args.update(desc=args)
    store_experiment(args, rollback_command('chaosbladeJvm-rollback.sh', args), delay_msg, stderr)


def chaosblade_jvm_prepare(args, kube_config, namespace, pod):
    api_instance = prepare_api(kube_config)
    check_result, _ = check_chaosblade_exists(api_instance, namespace, pod)
    print('Check result', check_result)
    if check_result == 'False':
        print('Copy file')
        copy_tar_file_to_namespaced_pod(api_instance, namespace, pod, resource_path('./resources/chaosblade-exec'),
                                        '/opt/chaosblade')
        copy_tar_file_to_namespaced_pod(api_instance, namespace, pod, resource_path('./resources/chaosblade-jvm'),
                                        '/opt/chaosblade')
        copy_tar_file_to_namespaced_pod(api_instance, namespace, pod, resource_path('./resources/chaosblade-module'),
                                        '/opt/chaosblade')
        out, err = executor_command_inside_namespaced_pod(api_instance, namespace, pod, [
            "bash", "-c",
            "chmod -R 755 /opt/chaosblade"
        ])
    else:
        print('Chaosblade Exist')
    print('Copy file finished')
    prepare_args = {'process': 'java'}
    prepare_command = chaosblade_prepare_script(chaosblade_prepare, prepare_args)
    print(prepare_command)
    prepare_msg, stderr = executor_command_inside_namespaced_pod(api_instance, namespace, pod, prepare_command)
    print(prepare_msg, stderr)
    agent_uid = jsonpath.jsonpath(json.loads(prepare_msg), 'result')
    print('agent', agent_uid)
    return agent_uid[0], api_instance, stderr


def check_chaosblade_exists(api_instance, namespace, pod):
    commands = ["bash",
                "-c",
                "[ -d /opt/chaosblade ] && echo True || echo False"]
    check_msg, check_err = executor_command_inside_namespaced_pod(api_instance, namespace, pod, commands)
    return check_msg, check_err


def ssh_executor(ip, user, pwd, command):
    ssh = paramiko.SSHClient()
    key = paramiko.AutoAddPolicy()
    ssh.set_missing_host_key_policy(key)
    ssh.connect(ip, 22, user, pwd, timeout=5)
    return ssh.exec_command(command)


def chaosblade_ssh_executor(ip, user, pwd, command, experiment_name):
    args = locals()
    ssh = paramiko.SSHClient()
    key = paramiko.AutoAddPolicy()
    ssh.set_missing_host_key_policy(key)
    ssh.connect(ip, 22, user, pwd, timeout=5)
    stdin, stdout, stderr = ssh_executor(ip, user, pwd, command)
    exec_msg = stdout.readline().replace('\n', '')
    experiment_uid = jsonpath.jsonpath(json.loads(exec_msg), 'result')
    args['rollback_command'] = '/opt/chaosblade/blade destroy ' + experiment_uid[0]
    store_experiment(args, rollback_command('chaosblade-ssh-rollback.sh', args), exec_msg, stderr.read().decode())


def chaosblade_ssh_jvm_executor(ip, user, pwd, process_name, pid, classname, methodname, script_file,
                                script_name,
                                experiment_name):
    args = locals()
    ssh = paramiko.SSHClient()
    key = paramiko.AutoAddPolicy()
    ssh.set_missing_host_key_policy(key)
    ssh.connect(ip, 22, user, pwd, timeout=5)
    prepare_args = {'pid': pid}
    prepare_command = chaosblade_prepare_script_vm(chaosblade_prepare, prepare_args)
    stdin, stdout, stderr = ssh_executor(ip, user, pwd, prepare_command)
    prepare_msg = stdout.readline().replace('\n', '')
    print(prepare_command)
    print(prepare_msg, stderr.readlines())
    agent_uid = jsonpath.jsonpath(json.loads(prepare_msg), 'result')
    inject_command = chaosblade_prepare_script_vm(chaosblade_inject, args)
    stdin, stdout, stderr = ssh_executor(ip, user, pwd, inject_command)
    inject_msg = stdout.readline().replace('\n', '')
    experiment_uid = jsonpath.jsonpath(json.loads(inject_msg), 'result')
    print('exe', experiment_uid)
    print('agent', agent_uid)
    # Save the UID which blade create
    args.update(agent_uid=agent_uid[0], experiment_uid=experiment_uid[0])
    args.update()
    store_experiment(args, rollback_command('chaosblade-ssh-jvm-rollback.sh', args), inject_msg, stderr.read().decode())
