
TEST_SCRIPTS := $(wildcard test/*.py)
TARGET_SCRIPTS := $(filter-out test/__init__.py,$(TEST_SCRIPTS) )

all: $(TARGET_SCRIPTS:.py=.py_tested)

%.py_tested: %.py 
	python3 -m unittest -v -f $(subst .py,, $(subst /,.,$<)) && touch $@
