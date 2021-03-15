# Project makefile

# working directories and files
#
TOPDIR	:=$(shell pwd)
DOCS	:=$(TOPDIR)/docs
BUILD	:=$(TOPDIR)/site
TEMPCFG	:=$(TOPDIR)/_mkdocs.yml

.PHONY: src doc test clean

nav:
	@export PYTHONIOENCODING=utf-8
	@cat mkdocs.yml > "$(TEMPCFG)"
	@python nav.py $(DOCS) | cat >> "$(TEMPCFG)"

serve: nav
	mkdocs serve -f "$(TEMPCFG)"

build: nav
	@mkdocs build -f "$(TEMPCFG)"


clean:
	@if [ -d "$(BUILD)" ];  then rm -rf "$(BUILD)" ; fi
	@if [ -e "$(TEMPCFG)" ];  then rm -rf "$(TEMPCFG)" ; fi