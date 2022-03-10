# check helm
tar zxvf ./example/helm/helm-v3.8.0-linux-amd64.tar.gz -C ./example/helm/

# install chaos-operator
./example/helm/linux-amd64/helm install chaosblade-operator ./example/chaosblade-operator/chaosblade-operator-1.5.0-ignore-webhook-error.tgz --namespace chaosblade

# install book-demo
kubectl apply -f ./example/bookdemo/all-in-one.yaml