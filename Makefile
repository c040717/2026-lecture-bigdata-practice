# Introduction to Big Data - labs
#   make image    build the Ubuntu lab image (once)
#   make shell    a shell inside the container
#   make wNN      show that week's README
#   make spark    check whether the optional task 4s can run here
#   make check    format-check every week you have results for
#   make test     run every week's test_tasks.py

SHELL := /bin/bash

image:
	docker build -t bigdata-lab .

shell:
	docker run -it --rm -v "$$PWD:/work" bigdata-lab bash

w02 w03 w04 w05 w06 w07:
	@d=$$(ls -d $@-*); echo "=== $$d ==="; cat $$d/README.md

check:
	@for d in w0*/; do \
	  w=$${d%%-*}; \
	  if [ -d "$$d/out" ]; then echo "=== $$d"; python3 check.py $$w; fi; \
	done

test:
	@for d in w0*/; do \
	  if [ -f "$$d/test_tasks.py" ]; then \
	    echo "=== $$d"; (cd $$d && python3 test_tasks.py) || true; \
	  fi; \
	done

spark:
	@echo "== java"; java -version 2>&1 | head -1 || echo "  no java"
	@echo "== pyspark"; python3 -c "import pyspark; print('  ', pyspark.__version__)" \
	  2>/dev/null || echo "   not installed - pip install pyspark"
	@echo
	@echo "Spark needs Java 8, 11 or 17. A newer JDK fails with a gateway error."
	@echo "The optional task 4s are in w02-mapreduce, w05-pagerank, w06-apriori."

.PHONY: image shell check test w02 w03 w04 w05 w06 w07
