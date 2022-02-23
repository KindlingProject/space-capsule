cat << EOF | kubectl create -f -
{{ k8s_resources }}
EOF