.PHONY: build upload install


## 编译为Py包
build:
	pip install build && pip install twine && python -m build

## 上传至PyPi，需要提前注册
upload:
	twine upload dist/jup_swap-0.1.5-py3-none-any.whl
	#twine upload dist/*

## 本地安装调试
install:
	pip install $(shell ls -1t dist/*.whl | head -n 1)


## Show help
help:
	@echo ''
	@echo 'Usage:'
	@echo ' make target'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
	helpMessage = match(lastLine, /^## (.*)/); \
	if (helpMessage) { \
	helpCommand = substr($$1, 0, index($$1, ":")-1); \
	helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
	printf " %-20s %s\n", helpCommand, helpMessage; \
	} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)
