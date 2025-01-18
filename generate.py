#!/usr/bin/env python3

import datetime
import json
import logging
import os
import stat
import xml.etree.cElementTree as ET

logging.basicConfig(level = logging.INFO)

output = "unidmenu"

categories = {
  "Lu": "Uppercase Letter",
  "Ll": "Lowercase Letter",
  "Lt": "Titlecase Letter",
  "LC": "Cased Letter",
  "Lm": "Modifier Letter",
  "Lo": "Other Letter",
  "L": "Letter",
  "Mn": "Nonspacing Mark",
  "Mc": "Spacing Mark",
  "Me": "Enclosing Mark",
  "M": "Mark",
  "Nd": "Decimal Number",
  "Nl": "Letter Number",
  "No": "Other Number",
  "N": "Number",
  "Pc": "Connector Punctuation",
  "Pd": "Dash Punctuation",
  "Ps": "Open Punctuation",
  "Pe": "Close Punctuation",
  "Pi": "Initial Punctuation",
  "Pf": "Final Punctuation",
  "Po": "Other Punctuation",
  "P": "Punctuation",
  "Sm": "Math Symbol",
  "Sc": "Currency Symbol",
  "Sk": "Modifier Symbol",
  "So": "Other Symbol",
  "S": "Symbol",
  "Zs": "Space Separator",
  "Zl": "Line Separator",
  "Zp": "Paragraph Separator",
  "Z": "Separator",
  "Cc": "Control",
  "Cf": "Format",
  "Cs": "Surrogate",
  "Co": "Private Use",
  "Cn": "Unassigned",
  "C": "Other",
}

# def charName(char):
#   name = char.attrib["na"]
#   if name == "":
#     name = "<control>"
#   return name


def charNameOrOldName(char):
  name = char.attrib["na"]
  if name == "":
    name = char.attrib["na1"]
  if name == "":
    for alias in char.findall("{http://www.unicode.org/ns/2003/ucd/1.0}name-alias"):
      if alias.attrib["type"] != "abbreviation":
        name = alias.attrib["alias"]
  return name


def charTitle(char):
  return charNameOrOldName(char) + " (U+" + char.attrib["cp"] + ")"


def charLink(char):
  return "<a href='%s'>%s</a>" % (char.attrib["cp"] + ".html", "U+" + char.attrib["cp"])


def charLinks(c, chars):
  return " ".join([charLink(chars[int(char, 16)]) for char in c.split(" ")])


def charPrintable(char):
  return char.attrib["gc"] not in ["Cc", "Cn"]


root = ET.parse('ucd.nounihan.flat.xml').getroot()
title = root.find("{http://www.unicode.org/ns/2003/ucd/1.0}description")
assert title is not None and title.text is not None
title_cs = title.text.split(" ")
assert len(title_cs) == 2 and title_cs[0] == "Unicode"
unicode_version = title_cs[-1]
version = "%s/%s" % (unicode_version, datetime.datetime.now(datetime.timezone.utc).isoformat())
logging.info("generating script version %s", version)

with open("cldr-annotations.json", "r", encoding = "utf-8") as f:
  annotations = json.loads(f.read())["annotations"]["annotations"]

chars = {}
for char in root.findall(
  "{http://www.unicode.org/ns/2003/ucd/1.0}repertoire/{http://www.unicode.org/ns/2003/ucd/1.0}char"
):
  if "cp" in char.attrib:
    chars[int(char.attrib["cp"], 16)] = char

with open(output, "w") as f:
  f.write(
    """#!/bin/bash

#MENU="wofi --show dmenu -i"
#MENU="wmenu -l 20 -i"
#MENU="tofi"
MENU="fuzzel --dmenu --hide-before-typing"

# https://github.com/dln/wofi-emoji/raw/master/wofi-emoji
sed '1,/^### DATA ###$/d' $0 | $MENU | cut -d ' ' -f 1 | tr -d '\n' | wtype -
exit
### DATA ###
"""
  )
  for _, char in chars.items():
    printable = charPrintable(char)
    if not printable:
      continue
    cp = char.attrib["cp"]
    s = chr(int(cp, 16))
    if s == " ":
      continue
    title = charTitle(char)
    indexName = charTitle(char)
    aliases = set()
    annotation = annotations.get(s)
    if annotation is not None:
      lowerCharName = charNameOrOldName(char).lower()
      for a in annotation["default"]:
        # Only add aliases that are not part of the actual name
        if a.lower() not in lowerCharName:
          aliases.add(a)
    if len(aliases) > 0:
      indexName += " (%s)" % ", ".join(aliases)
    indexName = s + " " + indexName
    f.write(indexName)
    f.write("\n")

st = os.stat(output)
os.chmod(output, st.st_mode | stat.S_IEXEC)
