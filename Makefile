# Introduction to Big Data - labs
#   make image    build the Ubuntu lab image (once)
#   make shell    a shell inside the container
#   make wNN      show that week's README
#   make check    format-check every week you have results for
#   make test     run every week's test_tasks.py

SHELL := /bin/bash

image:
	docker build -t bigdata-lab .

shell:
	docker run -it --rm -v "$$PWD:/work" bigdata-lab bash

w03 w04 w05 w06 w07:
	@d=$$(ls -d $@-*); echo "=== $$d ==="; cat $$d/README.md

check:
	@for d in w0*/; do \
	  w=$${d%%-*}; \
	  if [ -d "$$d/out" ]; then echo "=== $$d"; python3 check.py $$w; fi; \
	done

test:
	@for d in w0*/; do \
	  echo "=== $$d"; (cd $$d && python3 test_tasks.py) || true; \
	done

.PHONY: image shell check test w03 w04 w05 w06 w07
