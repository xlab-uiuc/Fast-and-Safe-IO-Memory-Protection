# Top level makefile, the real shit is at src/Makefile

default: all

.DEFAULT:
	cd src && $(MAKE) $@
	cd src-nc && $(MAKE) $@

install:
	cd src && $(MAKE) $@
	cd src-nc && $(MAKE) $@

.PHONY: install
