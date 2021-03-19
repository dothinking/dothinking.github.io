# Project makefile

# working directories and files
#
TOPDIR		:=$(shell pwd)
DOCS		:=$(TOPDIR)/docs
BUILD		:=$(TOPDIR)/build
BUILDDOCS	:=$(BUILD)/docs
MKDOCSCFG	:=_mkdocs.yml
CATEGORIES	:=categories
YEARS		:=years
NAVCNT		:=5
INDEXCNT	:=5
SERVECFG	:=$(TOPDIR)/$(MKDOCSCFG)
BUILDCFG	:=$(BUILD)/$(MKDOCSCFG)



.PHONY: pre_process
pre_process: 
	@echo Checking and creating sub-directories...
	@if [ -d "$(DOCS)/$(CATEGORIES)" ];  then rm -rf "$(DOCS)/$(CATEGORIES)" ; fi
	@if [ -d "$(DOCS)/$(YEARS)" ];  then rm -rf "$(DOCS)/$(YEARS)" ; fi
	@mkdir "$(DOCS)/$(CATEGORIES)"
	@mkdir "$(DOCS)/$(YEARS)"	


.PHONY: copy
copy: pre_process
	@if [ -d "$(BUILD)" ];  then rm -rf "$(BUILD)" ; fi
	@mkdir "$(BUILD)"
	@cp -rp "$(DOCS)" "$(BUILD)/"


.PHONY: serve
serve: pre_process
	@echo Summarizing pages...
	@cat mkdocs.yml > "$(SERVECFG)"
	@python run.py serve "$(DOCS)" $(YEARS) $(CATEGORIES) $(NAVCNT) $(INDEXCNT)  >> "$(SERVECFG)"
	@mkdocs serve -f "$(SERVECFG)"


.PHONY: build
build: copy
	@echo Summarizing pages...
	@cat mkdocs.yml > "$(BUILDCFG)"
	@python run.py build "$(BUILDDOCS)" $(YEARS) $(CATEGORIES) $(NAVCNT) $(INDEXCNT)  >> "$(BUILDCFG)"
	@mkdocs build -f "$(BUILDCFG)"


.PHONY: clean
clean:
	@if [ -d "$(BUILD)" ];  then rm -rf "$(BUILD)" ; fi
	@if [ -d "$(DOCS)/$(CATEGORIES)" ];  then rm -rf "$(DOCS)/$(CATEGORIES)" ; fi
	@if [ -d "$(DOCS)/$(YEARS)" ];  then rm -rf "$(DOCS)/$(YEARS)" ; fi
	@if [ -e "$(SERVECFG)" ];  then rm -rf "$(SERVECFG)" ; fi