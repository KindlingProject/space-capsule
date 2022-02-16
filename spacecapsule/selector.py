import json
import shlex
import jsonpath
from kubernetes import client, config
from subprocess import Popen, PIPE

import os
import sys

from jinja2 import Environment, FileSystemLoader

from spacecapsule.template import resource_path

script_file_directory = resource_path('./resources/templates/scripts')
script_env = Environment(loader=FileSystemLoader(searchpath=script_file_directory))
script_env.trim_blocks = True


def get_resources(args, needs):
    params = needs.split('@')
    script_template_file = 'getResources.sh'
    script_template = script_env.get_template(script_template_file)

    script = script_template.render(args)
    process = Popen(script, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = process.communicate()
    if len(err) > 0:
        print(err.decode())
        return -1
    resources = json.loads(out)
    # TODO resourceName is not specified
    # TODO multiNeeds
    # kind = jsonpath.jsonpath(resources, '$.kind')
    need = jsonpath.jsonpath(resources, params[1])

    return [need]



