NAME = script.elementum.nova
GIT = git
GIT_VERSION = $(shell $(GIT) describe --abbrev=0 --tags)
TAG_VERSION = $(subst v,,$(GIT_VERSION))
LAST_COMMIT = $(shell $(GIT) log -1 --pretty=\%B)
VERSION = $(shell sed -ne "s/.*COLOR\]\"\sversion=\"\([0-9a-z\.\-]*\)\".*/\1/p" addon.xml)
ZIP_SUFFIX = zip
ZIP_FILE = $(NAME)-$(VERSION).$(ZIP_SUFFIX)

all: clean zip

$(ZIP_FILE):
	$(GIT) archive --format zip -0 --prefix $(NAME)/ --output $(ZIP_FILE) HEAD
	rm -rf $(NAME)

zip: $(ZIP_FILE)

clean_arch:
	 rm -f $(ZIP_FILE)

clean:
	rm -f $(ZIP_FILE)
	rm -rf $(NAME)

surge:
	$(GIT) clone --depth=1 https://bitbucket.com/Tw1cker/nova-site.git
	sed -i "s/version\s=\s\"\([0-9a-z\.\-]*\)\"/version = \"${VERSION}\"/" nova-site/public/index.jade
	cd nova-site && harp compile . html/
	mkdir -p nova-site/html/release/$(NAME)
	cp addon.xml changelog.txt icon.png fanart.jpg nova-site/html/release/$(NAME)
	cp *.zip nova-site/html/release/$(NAME)
	cd nova-site && surge html nemiroff.surge.sh