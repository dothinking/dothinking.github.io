# Project makefile

# working directories and files
#
TOPDIR	:=$(shell pwd)
DOCS	:=$(TOPDIR)/docs
BUILD	:=$(TOPDIR)/site
TEMPCFG	:=$(TOPDIR)/_mkdocs.yml
TEMPDIR :=_categories

.PHONY: serve


sub_path: 
	@if [ -d "$(DOCS)/$(TEMPDIR)" ];  then rm -rf "$(DOCS)/$(TEMPDIR)" ; fi
	@mkdir "$(DOCS)/$(TEMPDIR)"

nav: sub_path
	@cat mkdocs.yml > "$(TEMPCFG)"
	@python nav.py "$(DOCS)" $(TEMPDIR) | cat >> "$(TEMPCFG)"

serve: nav
	mkdocs serve -f "$(TEMPCFG)"

build: nav
	@mkdocs build -f "$(TEMPCFG)"


clean:
	@if [ -d "$(BUILD)" ];  then rm -rf "$(BUILD)" ; fi
	@if [ -d "$(DOCS)/$(TEMPDIR)" ];  then rm -rf "$(DOCS)/$(TEMPDIR)" ; fi
	@if [ -e "$(TEMPCFG)" ];  then rm -rf "$(TEMPCFG)" ; fi