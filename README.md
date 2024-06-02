# dtd2rst

Generate a framework of reStructuredText pages for a DTD documentation.

![Screenshot](docs/Screenshots/screen01.png)

## Features

- Creates one page per XML tag, named after the tag.
  Each page has a framework for documentation:
  
  - A first-level heading, containing the tag name.
  
  - A box containing the basic information:
      - Purpose (to be filled in manually).
      - A list of attributes (chapter links).
      - A list of contained elements (page links).
      
  - A second-level chapter for each attribute.
  - Information about each attribute (to be completed manually).
  
- Creates an index page with all tags.

## Requirements

- Python v3.6+
- The [lxml package](https://pypi.org/project/lxml/)

## Download

Save the file [dtd2rst.py](https://raw.githubusercontent.com/peter88213/dtd2rst/main/src/dtd2rst.py).


## Usage
```
    dtd2rst.py <DTD path>

```

------------

## License

Published under the [MIT License](https://opensource.org/licenses/mit-license.php)
