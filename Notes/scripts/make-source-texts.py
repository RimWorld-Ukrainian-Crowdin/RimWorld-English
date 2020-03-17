#!/usr/bin/env python3
import os
import os.path

from lxml import etree


def main(args):
    """Copy text from xml comments into tags."""
    translations_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    for dirpath, dirnames, filenames in os.walk(translations_root):
        if "/." in dirpath:
            continue  # skip hidden directories
        for file_name in filenames:
            if not file_name.endswith(".xml"):
                continue
            file_path = os.path.join(dirpath, file_name)
            transform_file(file_path)


def transform_file(file_path):
    print("Transforming file ", file_path)
    with open(file_path, "rb") as inf:
        parser = etree.XMLParser(recover=True)
        doc = etree.parse(inf, parser)

    # Replace tag text with last comment text
    last_comment = None
    for el in list(doc.iter()):
        text = (el.text or "").strip()

        if isinstance(el, etree._Comment) and text.startswith("EN:"):
            text = el.text[len("EN:") + 1 :]
            # Strip whitespace only around single-line texts
            if not text.startswith("\n"):
                text = text.strip()
            last_comment = text
        else:
            if last_comment is not None:
                el.text = last_comment
                if el.tag in [
                    "MessageModNeedsWellFormattedTargetVersion",
                    "MessageModNeedsWellFormattedPackageId",
                ]:
                    # These texts contain XML examples that are more readable
                    # without escaping "<" and ">"
                    el.text = etree.CDATA(el.text)
                # If the text contains any tags, we want them to be replaced by
                # the new text tags, so the element children must be removed.
                for _el in list(el.iterdescendants()):
                    _el.getparent().remove(_el)

            last_comment = None

    with open(file_path, "wb") as outf:
        doc_content = b'\xEF\xBB\xBF<?xml version="1.0" encoding="UTF-8"?>\n'
        doc_content += etree.tostring(doc, encoding="UTF-8")
        # "<" and ">" is technically a reserved character and should be escaped when
        # included into XML text. We are undoing LXML's escaping in order to
        # keep the original text appearance for better readability.
        known_tags = [b"li", b"rulesStrings", b"Name"]
        for tagName in known_tags:
            doc_content = doc_content.replace(
                b"&lt;" + tagName + b"&gt;", b"<" + tagName + b">"
            )
            doc_content = doc_content.replace(
                b"&lt;/" + tagName + b"&gt;", b"</" + tagName + b">"
            )
        # Rules expressions. "<=" breaks the game's XML parser, so it is not
        # replaced here.
        doc_content = doc_content.replace(b"-&gt;", b"->")
        doc_content = doc_content.replace(b"&gt;=", b">=")

        outf.write(doc_content)


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
