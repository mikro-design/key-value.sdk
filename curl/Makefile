SHELL := /bin/bash

BASE_URL ?= https://key-value.co
TOKEN ?=
SKIP_DELETE ?=

.PHONY: curl-example
curl-example:
	@echo "Running curl example against $(BASE_URL)"
	@BASE_URL="$(BASE_URL)" \
	TOKEN="$(TOKEN)" \
	SKIP_DELETE="$(SKIP_DELETE)" \
	bash run.sh
