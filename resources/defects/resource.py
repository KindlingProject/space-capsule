import click
from spacecapsule.selector import get_resources
from spacecapsule.executor import bash_executor
from spacecapsule.template import resource_limit, kubectl_script, k8s_resource, namespace_quota_yaml, \
    k8s_resource_script, network_policy_yaml


def resource(namespace, resource_type, resource_name, experiment_name, container, limits, requests, desc):
    args = locals()
    # defects_info(args)
    args['desc'] = 'resource:' + desc
    bash_executor(kubectl_script, resource_limit, rollback_args, 'kubectl-rollback.sh', args)


def namespace_quota(namespace, cpu_limits, cpu_requests, mem_requests, mem_limits, experiment_name, desc):
    args = locals()
    args['desc'] = 'namespace_quota:' + desc
    bash_executor(k8s_resource_script, namespace_quota_yaml, rollback_args2, 'k8sResource-rollback.sh', args)

def network_policy(namespace, label_name, label_value,experiment_name,desc):
    args = locals()
    args['desc'] = 'network_policy:' + desc
    bash_executor(k8s_resource_script, network_policy_yaml, rollback_args2, 'k8sResource-rollback.sh', args)

def rollback_args(args):
    need = args['resource_type'] + '@$.metadata.annotations'
    anno = get_resources(args, need)
    version = anno[0][0]['deployment.kubernetes.io/revision']
    return {'history_version': int(version) - 1}


def rollback_args2(args):
    return {}