import configparser
import os.path
import shlex
import time
from subprocess import Popen, PIPE

from jinja2 import Environment, FileSystemLoader

from spacecapsule.template import resource_path

template_file_directory = resource_path('./resources/templates')
template_env = Environment(loader=FileSystemLoader(searchpath=template_file_directory))
template_env.trim_blocks = True
script_file_directory = resource_path('./resources/templates/scripts')
script_env = Environment(loader=FileSystemLoader(searchpath=script_file_directory))
script_env.trim_blocks = True

history_path = os.path.abspath("./history")

RUNNING = "RUNNING"
DESTROY = "DESTROY"
ERROR = "ERROR"


def update_experiment_status(experiment, args):
    status_path = os.path.join(history_path, experiment, 'defect-status')
    config = configparser.ConfigParser()
    config.read(status_path)
    pre_status = config['STATUS']
    for key in args:
        pre_status[key] = args[key]
    with open(status_path, 'w') as configfile:
        config.write(configfile)


def check_status(ctx, param, value):
    if not check_experiment_undo(ctx.command.name):
        print("Please undo last experiment!")
        show_experiment(ctx.command.name)
        exit(0)
    return


def check_experiment_undo(experiment):
    status_path = os.path.join(history_path, experiment, 'defect-status')
    if os.path.exists(status_path):
        config = configparser.ConfigParser()
        config.read(status_path)
        pre_status = config['STATUS']
        if pre_status['status'] == RUNNING:
            return False
        else:
            return True
    else:
        return True


def record_case_info(experiment, args):
    config = configparser.ConfigParser()
    config['STATUS'] = {
        "status": RUNNING,
        'create_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }
    config["INFO"] = {
        'experiment_name': args['experiment_name'],
        'desc': args['desc'],
    }
    status_path = os.path.join(history_path, experiment, 'defect-status')
    with open(status_path, 'w') as configfile:
        config.write(configfile)


def rollback_command(command_template_file, args):
    template = script_env.get_template(command_template_file)
    return template.render(args)


def store_experiment(args, rollback_cmd, cmd_out, cmd_err):
    defect_path = os.path.join(history_path, args['experiment_name'])
    if not os.path.exists(defect_path):
        os.makedirs(defect_path)
    record_case_info(args['experiment_name'], args)

    rollback_path = os.path.join(defect_path, 'rollback.sh')
    with open(rollback_path, 'w') as info:
        info.write(rollback_cmd)
    with open(os.path.join(defect_path, 'command.log'), 'a') as out:
        if cmd_out is not None:
            out.write(cmd_out)
    with open(os.path.join(defect_path, 'command.err'), 'a') as err:
        if cmd_err is not None:
            err.write(cmd_err)


def list_experiment():
    for _, dirs, _ in os.walk(history_path):
        for dir_name in dirs:
            print(dir_name)


def show_experiment(experiment):
    status_path = os.path.join(history_path, experiment, 'defect-status')
    config = configparser.ConfigParser()
    config.read(status_path)
    pre_status = config['STATUS']
    pre_info = config['INFO']
    infos = {}
    for key in pre_status:
        infos[key] = pre_status[key]
    for key in pre_info:
        infos[key] = pre_info[key]
    info_template = 'defectInfo'
    template = template_env.get_template(info_template)
    defect_info = template.render(infos)
    print(defect_info)


def undo_experiment(experiment):
    rollback_cmd_file = os.path.join(history_path, experiment, 'rollback.sh')
    with open(rollback_cmd_file, 'r') as cmd_file:
        cmd = cmd_file.read()
        process = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = process.communicate()
        update_experiment_status(experiment, {
            "status": DESTROY,
            "end_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        })
        print(out.decode())
        print(err.decode())
        return
