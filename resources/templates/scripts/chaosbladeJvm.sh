kubectl  cp  ./chaosblade-1.5.0/  practice/ng-7c8d6fb78b-dhgnq:/usr/local
kubectl  cp  ./ChaosService.java  practice/ng-7c8d6fb78b-dhgnq:/usr/local
kubectl exec -it ng-7c8d6fb78b-dhgnq -n  practice -- /usr/local/chaosblade-1.5.0/blade prepare jvm --process java
kubectl exec -it ng-7c8d6fb78b-dhgnq -n  practice -- /usr/local/chaosblade-1.5.0/blade status --type prepare --target jvm
kubectl exec -it ng-7c8d6fb78b-dhgnq -n  practice -- /usr/local/chaosblade-1.5.0/blade create jvm script --classname com.imooc.appoint.service.Impl.PracticeServiceImpl --methodname mysqlSuccess --script-file /usr/local/ChaosService.java --script-name specifyReturnOb
kubectl exec -it ng-7c8d6fb78b-dhgnq -n  practice -- /usr/local/chaosblade-1.5.0/blade status --type create --target jvm