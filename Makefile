# Project makefile

# working directories and files
#
TOPDIR		:=$(shell pwd)
DOCS		:=$(TOPDIR)/docs
BUILD		:=$(TOPDIR)/build

# mkdocs configuration file
MKDOCSCFG	:=_mkdocs.yml
SERVECFG	:=$(TOPDIR)/$(MKDOCSCFG)
BUILDCFG	:=$(BUILD)/$(MKDOCSCFG)

# sub-dir names for categoried posts
CATEGORIES	:=categories
YEARS		:=years

# count of items show in navigation bar
NAVCNT		:=5

# count of latest posts show in homepage
INDEXCNT	:=7



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
	@cp mkdocs.yml "$(SERVECFG)"
	@python run.py serve "$(SERVECFG)" $(YEARS) $(CATEGORIES) $(NAVCNT) $(INDEXCNT)
	@mkdocs serve -f "$(SERVECFG)"


.PHONY: build
build: copy
	@echo Summarizing pages...
	@cp mkdocs.yml "$(BUILDCFG)"
	@python run.py build "$(BUILDCFG)" $(YEARS) $(CATEGORIES) $(NAVCNT) $(INDEXCNT)
	@mkdocs build -f "$(BUILDCFG)"


.PHONY: clean
clean:
	@if [ -d "$(BUILD)" ];  then rm -rf "$(BUILD)" ; fi
	@if [ -d "$(DOCS)/$(CATEGORIES)" ];  then rm -rf "$(DOCS)/$(CATEGORIES)" ; fi
	@if [ -d "$(DOCS)/$(YEARS)" ];  then rm -rf "$(DOCS)/$(YEARS)" ; fi
	@if [ -e "$(SERVECFG)" ];  then rm -rf "$(SERVECFG)" ; fi