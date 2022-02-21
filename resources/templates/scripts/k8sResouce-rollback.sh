cat << EOF | kubectl delete -f -
{{ k8s_resources }}EOF