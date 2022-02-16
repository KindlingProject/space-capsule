from spacecapsule.history import store_experiment, defects_info, rollback_command
from subprocess import Popen, PIPE


def bash_executor(create_script, create_template, create_rollback_args, rollback_template_file, args):
    # TODO 部分参数需要executor选择
    script = create_script(create_template, args)
    process = Popen(script, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    out, err = process.communicate()

    args.update(create_rollback_args(args))
    store_experiment(args, rollback_command(rollback_template_file, args), out.decode(), err.decode())


def k8s_executor(k8s_instance, selectors, command):

    print('TODO')