import os
import sys
from typing import Callable

from jinja2 import Environment, FileSystemLoader


def resource_path(relative_path):
    """ Get absolute path to resource, works for both in IDE and for PyInstaller """
    # PyInstaller creates a temp folder and stores path in sys._MEIPASS
    # In IDE, the path is os.path.join(base_path, relative_path, file_name)
    # Search in Dev path first, then MEIPASS
    base_path = os.path.abspath(".")
    dev_dir_path = os.path.join(base_path, relative_path)
    if os.path.exists(dev_dir_path):
        return dev_dir_path
    else:
        dir_path = os.path.join(sys._MEIPASS, relative_path)
        if not os.path.exists(dir_path):
            msg = "\nError finding resource in either {} or {}".format(dev_dir_path, dir_path)
            print(msg)
            return None
        return dir_path


script_file_directory = resource_path('./resources/templates/scripts')
script_env = Environment(loader=FileSystemLoader(searchpath=script_file_directory))
script_env.trim_blocks = True
template_file_directory = resource_path('./resources/templates')
template_env = Environment(loader=FileSystemLoader(searchpath=template_file_directory))
template_env.trim_blocks = True


def kubectl_script(command_script: Callable, args):
    template_file_name = 'kubectl.sh'
    template = script_env.get_template(template_file_name)
    args['command'] = command_script(args)
    script = template.render(args)

    return script


def chaosblade_resource_script(command_script, args):
    template_file_name = 'chaosbladeResource.sh'
    template = script_env.get_template(template_file_name)
    args['blade_resources'] = command_script(args)
    script = template.render(args)
    return script


def chaosblade_prepare_script(command_script, args):
    template_file_name = 'chaosbladeJvm.sh'
    template = script_env.get_template(template_file_name)
    args['command'] = command_script(args)
    script = template.render(args)
    commands = [
        "bash",
        "-c",
        script
    ]
    return commands


def chaosblade_prepare_script_vm(command_script, args):
    template_file_name = 'chaosbladeJvm.sh'
    template = script_env.get_template(template_file_name)
    args['command'] = command_script(args)
    script = template.render(args)
    return script


def chaosblade_resource(args):
    template_file_name = 'chaosbladeResource.yaml'
    template = template_env.get_template(template_file_name)
    resource = template.render(args)
    return resource


def k8s_resource(args):
    template_file_name = 'k8sResource.yaml'
    template = template_env.get_template(template_file_name)
    resource = template.render(args)
    return resource


def resource_limit(args):
    template_file_name = 'resource.sh'
    template = template_env.get_template(template_file_name)
    command = template.render(args)
    return command


def namespace_quota_yaml(args):
    template_file_name = 'namespace_quota.yaml'
    template = template_env.get_template(template_file_name)
    command = template.render(args)
    return command

def network_policy_yaml(args):
    template_file_name = 'network_policy.yaml'
    template = template_env.get_template(template_file_name)
    command = template.render(args)
    return command

def chaosblade_prepare(args):
    template_file_name = 'blade_prepare.sh'
    template = template_env.get_template(template_file_name)
    command = template.render(args)
    return command


def chaosblade_inject(args):
    template_file_name = 'blade_inject.sh'
    template = template_env.get_template(template_file_name)
    command = template.render(args)
    return command


def chaosblade_jvm_delay(args):
    template_file_name = 'blade_delay.sh'
    template = template_env.get_template(template_file_name)
    command = template.render(args)
    return command


def k8s_resource_script(command_script, args):
    template_file_name = 'k8sResource.sh'
    template = script_env.get_template(template_file_name)
    args['k8s_resources'] = command_script(args)
    script = template.render(args)
    return script