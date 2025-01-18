DOCSET_NAME=UnicodeCharacters
DOCSET_DIR=$(DOCSET_NAME).docset
DOCSET_PACKAGE=$(DOCSET_NAME).tgz
DASH_DIR=dash

all: build

build: ucd.nounihan.flat.xml cldr-annotations.json
	python3 generate.py

.PHONY: clean
clean:

ucd.nounihan.flat.xml: 
	curl -s -S -O https://www.unicode.org/Public/UCD/latest/ucdxml/ucd.nounihan.flat.zip
	unzip ucd.nounihan.flat.zip
	rm ucd.nounihan.flat.zip

cldr-annotations.json:
	curl -s -S -o $@ https://raw.githubusercontent.com/unicode-org/cldr-json/refs/heads/main/cldr-json/cldr-annotations-full/annotations/en/annotations.json
