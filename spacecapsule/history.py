import os.path
import shlex
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


def defects_info(args):
    info_template = 'defectInfo'
    template = template_env.get_template(info_template)
    defect_info = template.render(args)
    defect_path = os.path.join(history_path, args['experiment_name'])
    if not os.path.exists(defect_path):
        os.makedirs(defect_path)
    info_path = os.path.join(defect_path, 'defect-info')
    with open(info_path, 'w') as info:
        info.write(defect_info)
    return defect_path


def rollback_command(command_template_file, args):
    template = script_env.get_template(command_template_file)
    return template.render(args)


def store_experiment(info, rollback_cmd, cmd_out, cmd_err):
    defect_path = defects_info(info)

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
    info_file = os.path.join(history_path, experiment, 'defect-info')
    with open(info_file, 'r') as info:
        print(info.read())


def undo_experiment(experiment):
    rollback_cmd_file = os.path.join(history_path, experiment, 'rollback.sh')
    with open(rollback_cmd_file, 'r') as cmd_file:
        cmd = cmd_file.read()
        process = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = process.communicate()
        print(out.decode())
        print(err.decode())
        return

