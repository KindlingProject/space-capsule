define exec-command
$(1)

endef

# CI build
.PHONY: build
build:
	-pip3 uninstall space-capsule -y
	pip3 install .
	pip3 install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
	pyinstaller cli.py --onefile --name space-capsule --add-data resources:resources