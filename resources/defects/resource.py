import click
from spacecapsule.selector import get_resources
from spacecapsule.executor import bash_executor
from spacecapsule.template import resource_limit, kubectl_script, k8s_resource


def resource(namespace, resource_type, resource_name, experiment_name, container, limits, requests):
    args = locals()
    # defects_info(args)
    bash_executor(kubectl_script, resource_limit, rollback_args, 'kubectl-rollback.sh', args)


def namespace_quota(namespace, cpu_limits, cpu_requests, mem_requests, mem_limits):
    args = locals()
    bash_executor(k8s_resource, namespace_quota, {}, 'k8sResource-rollback.sh', args)


def rollback_args(args):
    need = args['resource_type'] + '@$.metadata.annotations'
    anno = get_resources(args, need)
    version = anno[0][0]['deployment.kubernetes.io/revision']
    return {'history_version': int(version) - 1}
