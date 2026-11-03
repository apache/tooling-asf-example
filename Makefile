# TODO: Automatically build the .PHONY line
# TODO: Add documentation
.PHONY: build bump-dev bump-release check-dev check-release commit \
install prek update-deps

build:
	uv build

bump-dev:
	@# This assumes that we have the latest version of "asfexample"
	@# If not, run "uv pip install -e ." first
	uv run asfexample --bump-dev
	@# Suppress the warning about ignoring the existing lockfile
	rm -f uv.lock
	@# This writes the new stamp into the uv.lock file and upgrades the package
	@# We do not have to use --upgrade as that is only for dependencies
	uv sync

bump-release:
	@# This assumes that we have the latest version of "asfexample"
	@# If not, run "uv pip install -e ." first
	uv run asfexample --bump-release
	@# Suppress the warning about ignoring the existing lockfile
	rm -f uv.lock
	@# This writes the new stamp into the uv.lock file and upgrades the package
	@# We do not have to use --upgrade as that is only for dependencies
	uv sync

check-dev: prek bump-dev
	@# We run lint modifications first, then update the version
	@# We do not consider the following a lint as it runs all test cases always
	uv run pytest -q

check-release: prek bump-release
	@# We run lint modifications first, then update the version
	@# We do not consider the following a lint as it runs all test cases always
	uv run pytest -q


commit:
	git add -A
	git commit
	git pull
	git push

install:
	uv pip install -e .

prek:
	git add -A
	PREK_SKIP=version uv run prek run --all-files

update-deps:
	uv lock --upgrade
	uv sync
