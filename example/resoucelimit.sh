# 为 test-ns 下的 testdemo1 这个deployment的testdemo1 容器设置资源限制
# space-capsule resources {ns} {resources-kind} {resources-name} {container-name} [OPTION] {experiment-name}
# OPTION:
#     --container
#     --limits
#     --requests
space-capsule resources test-ns deploy testdemo1 -container testdemo1 \
  --limit cpu=100,mem=100 --requests cpu=100,mem=100 resourceLimitTest

# space-capsule undo  {experiment-name}
space-capsule undo resourcesLimitTest