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
	mkdir -p ./build/space-capsule-alpha
	cp -r ./dist/space-capsule ./build/space-capsule-alpha/
	cp -r ./example ./build/space-capsule-alpha/
	cp install.sh ./build/space-capsule-alpha/
	tar -czvf space-capsule-alpha.tar.gz -C ./build space-capsule-alpha/