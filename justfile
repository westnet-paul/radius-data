VERSION := `uv version`

all: test git-tag git-push

test:
	python -m pytest --cov radiusdata --cov-report html:htmlcov

git-tag:
	[ -z `git tag | grep "^{{VERSION}}$$"` ] && \
	git tag -a {{VERSION}} -m "`git log -n1 --format=%s`" && \
	git push origin {{VERSION}} || true

git-push:
	git push
