"""Generate a framework of rst pages for a DTD documentation.

Features
--------

- Creates one page per XML tag, named after the tag.
  Each page has a framework for documentation:
  
  - A first-level heading, containing the tag name.
  
  - A box containing the basic information:
      - Purpose (to be filled in manually).
      - A list of attributes.
      - A list of contained elements (page links).
      
  - A second-level heading for each attribute.
  
- Creates an index page with all tags.
  
Usage
-----
    dtd2rst.py <DTD path>

Requirements
------------

- Python v3.6+
- The lxml package

https://lxml.de/validation.html#id1

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/
Published under the MIT License (https://opensource.org/licenses/mit-license.php)


Changelog:

v1.0.0 - Initial release.
v1.1.0 - Link to the attribute chapters within the pages. 
"""
import os
from shutil import rmtree
from string import Template
import sys

from lxml import etree

TITLE_UNDERLINER = '='

INDEX_HEADING = 'The $RootTag file format'
TAG_HEADING = 'The <$Tag> tag'
ATTRIBUTE_HEADING = 'The $Attribute attribute'
ATTRIBUTE_LINK = '#the-$Attribute-attribute'

TOCTREE = """
.. toctree::
   :maxdepth: 1
   :caption: XML tags
"""

INFO_BOX = """
.. admonition:: <$Tag>
   
   Purpose
$Attributes
$Content
"""


class Filenames:
    """Manage case-insensitive filenames."""

    def __init__(self):
        self._filenames = {}

    def add_key(self, key):
        filename = key.lower().replace(' ', '_')
        while filename in self._filenames.values():
            filename = f'_{filename}'
        self._filenames[key] = filename

    def get_filename(self, key):
        return self._filenames[key]


fn = Filenames()


def get_heading(heading, c):
    headingLines = []
    if c == TITLE_UNDERLINER:
        headingLines.append(c * len(heading))
    headingLines.append(heading)
    headingLines.append(c * len(heading))
    return '\n'.join(headingLines)


def read_dtd(dtdPath, dtdJson):
    """Populate a JSON data structure with the relevant DTD information."""

    def get_content(cnt):
        if cnt is None:
            return
        if cnt.name is not None:
            contents.append(cnt.name)
        if cnt.left is not None:
            get_content(cnt.left)
        if cnt.right is not None:
            get_content(cnt.right)

    dtd = etree.DTD(open(dtdPath, 'rb'))
    for element in dtd.iterelements():
        dtdJson[element.name] = {}
        contents = []
        get_content(element.content)
        dtdJson[element.name]['contents'] = contents
        dtdJson[element.name]['attributes'] = {}

        for attr in element.iterattributes():
            dtdJson[element.name]['attributes'][attr.name] = []
            dtdJson[element.name]['attributes'][attr.name].append(attr.type)
            dtdJson[element.name]['attributes'][attr.name].append(attr.default)
            dtdJson[element.name]['attributes'][attr.name].append(attr.values())
            dtdJson[element.name]['attributes'][attr.name].append(attr.default_value)

    print(f'DTD "{dtdPath}" successfully read.')


def write_index_page(rstPath, dtdJson):
    indexPageLines = []
    heading = Template(INDEX_HEADING).substitute({'RootTag':next(iter(dtdJson))})
    indexPageLines.append(get_heading(heading, TITLE_UNDERLINER))
    indexPageLines.append(TOCTREE)

    tags = sorted(dtdJson.keys())

    for tag in tags:
        fn.add_key(tag)
        indexPageLines.append(fn.get_filename(tag))

    fn.add_key(heading)
    indexPage = f"{rstPath}/{fn.get_filename(heading)}.rst"
    with open(indexPage, 'w', encoding='utf-8') as f:
        f.write('\n   '.join(indexPageLines))
    print(f'Index page "{indexPage}" written.')


def write_rst(rstPath, dtdJson):
    """Create pages from the dtdJson structure."""
    try:
        rmtree(rstPath)
    except:
        pass
    else:
        print(f'Existing directory "{rstPath}" deleted.')
    os.makedirs(rstPath)
    print(f'Empty directory "{rstPath}" created.')
    write_index_page(rstPath, dtdJson)
    for tag in dtdJson:
        tagJson = dtdJson[tag]
        write_tag_page(rstPath, tag, tagJson)


def write_tag_page(rstPath, tag, tagJson):
    tagPageLines = []
    heading = Template(TAG_HEADING).substitute({'Tag':tag})
    tagPageLines.append(get_heading(heading, TITLE_UNDERLINER))

    #--- Colored box with basic information.

    mapping = {'Tag':tag}

    # Collect attribute names.
    attributeLines = []
    for attributeName in tagJson['attributes']:
        mapping = {'Attribute':attributeName.lower()}
        attributeLink = f'`{attributeName} <{Template(ATTRIBUTE_LINK).substitute(mapping)}>`__'
        attributeLines.append(attributeLink)
    if attributeLines:
        attributeNames = '\n      - '.join(attributeLines)
        mapping['Attributes'] = f'\n   Attributes\n      - {attributeNames}'
    else:
        mapping['Attributes'] = ''

    # Collect content names.
    contentLines = []
    for contentName in tagJson['contents']:
        contentLink = f'`{contentName} <{fn.get_filename(contentName)}.html>`__'
        contentLines.append(contentLink)
    if contentLines:
        contentNames = '\n      - '.join(contentLines)
        mapping['Content'] = f'\n   Content\n      - {contentNames}'
    else:
        mapping['Content'] = ''

    tagPageLines.append(f'   {Template(INFO_BOX).safe_substitute(mapping)}')

    #--- One chapter per attribute.

    for attributeName in tagJson['attributes']:
        attributeHeading = Template(ATTRIBUTE_HEADING).substitute({'Attribute':attributeName})
        tagPageLines.append(f'{get_heading(attributeHeading, "-")}\n')

        attrType = tagJson['attributes'][attributeName][0]
        attrDefault = tagJson['attributes'][attributeName][1]
        attrValues = tagJson['attributes'][attributeName][2]
        defaultValue = tagJson['attributes'][attributeName][3]

        if attrType == 'enumeration':
            for literal in attrValues:
                tagPageLines.append(f'- {literal}: ')
            tagPageLines.append(f'\nDefault value: {defaultValue}\n')
        else:
            tagPageLines.append(f'Default: {attrDefault}\n')

    #--- Write the page to a rst file.

    tagPage = f"{rstPath}/{fn.get_filename(tag)}.rst"
    with open(tagPage, 'w', encoding='utf-8') as f:
        f.write('\n'.join(tagPageLines))
    print(f'Tag page "{tagPage}" written.')


def main(dtdPath):
    dtdJson = {}
    read_dtd(dtdPath, dtdJson)
    rstPath = os.path.join(os.path.dirname(dtdPath), 'dtd-docs')
    write_rst(rstPath, dtdJson)


if __name__ == '__main__':
    main(sys.argv[1])

