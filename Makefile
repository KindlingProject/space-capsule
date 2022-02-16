define exec-command
$(1)

endef

# CI build
.PHONY: build
build:
	pyinstaller cli.py --onefile --name space-capsule --add-data resources:resources