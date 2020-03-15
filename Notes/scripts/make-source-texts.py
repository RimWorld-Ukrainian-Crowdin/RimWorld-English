#!/usr/bin/env python3
import argparse
import os
import os.path
import tempfile
import urllib.request
import xml.sax
import zipfile

from lxml import etree


def main(args):
    """Copy text from xml comments into tags."""
    translations_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    for dirpath, dirnames, filenames in os.walk(translations_root):
        if '/.' in dirpath:
            continue  # skip hidden directories
        for file_name in filenames:
            if not file_name.endswith(".xml"):
                continue
            file_path = os.path.join(dirpath, file_name)
            transform_file(file_path)


def transform_file(file_path):
    print('Transforming file ', file_path)
    with open(file_path, "rb") as inf:
        doc = etree.parse(inf)

    # Replace tag text with last comment text
    last_comment = None
    for el in doc.iter():
        if isinstance(el, etree._Comment) and el.text.startswith(" EN: "):
            last_comment = el.text[len(" EN: ") :].strip()
        else:
            if last_comment is not None:
                el.text = last_comment
            last_comment = None

    with open(file_path, "wb") as outf:
        outf.write(b'\xEF\xBB\xBF<?xml version="1.0" encoding="UTF-8"?>\n')
        outf.write(etree.tostring(doc, encoding="UTF-8"))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
