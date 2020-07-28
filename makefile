
TEST_SCRIPTS := $(wildcard test/*.py)
TARGET_SCRIPTS := $(filter-out test/__init__.py,$(TEST_SCRIPTS) )

all: $(TARGET_SCRIPTS:.py=.py_tested)

%.py_tested: %.py 
	python -m unittest -v -f $(subst .py,, $(subst /,.,$<)) && touch $@

clean:
	-rm test/*.py_tested
	-rm test/*.pyc
