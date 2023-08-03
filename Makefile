PY_FILES   = $(shell find . -type f -name '*.py')
VERSION = $(shell grep "__version__ =" querier/__init__.py | cut -d '"' -f2)
SDIST   = dist/querier-$(VERSION).tar.gz

.PHONY: all sdist docker install_module install_service install uninstall_module uninstall_service uninstall

all:
	@echo "Nothing to build"

$(SDIST): $(PY_FILES)
	@echo "Building source distribution"
	python3 setup.py sdist

docker: $(SDIST)
	@echo "Building Docker image"
	docker build -t igmp-querier .

install_module:
	@echo "Installing Python module"
	python3 setup.py install --record files.txt

install_service:
	@echo "Installing QuerierD service"
	cp lib/systemd/system/querierd.service /lib/systemd/system
	systemctl daemon-reload
	systemctl start querierd.service
	systemctl enable querierd.service

install: install_module install_service

uninstall_module:
	@echo "Removing Python module"
	cat files.txt | xargs rm -rf
	rm files.txt

uninstall_service:
	@echo "Uninstalling QuerierD service"
	systemctl stop querierd.service
	systemctl disable querierd.service
	rm /lib/systemd/system/querierd.service

uninstall: uninstall_module uninstall_service
