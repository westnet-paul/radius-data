VERSION := `uv version | cut -d' ' -f2`
	
all: test git-status git-tag git-push

test:
	python -m pytest --cov radiusdata --cov-report html:htmlcov

git-status:
	[[ -z "$(git status -s)" ]]

git-tag:
	[ -z `git tag | grep "^{{VERSION}}$$"` ] && \
	git tag -a {{VERSION}} -m "`git log -n1 --format=%s`" && \
	git push origin {{VERSION}} || true

git-push:
	git push
