# syosetu2epub
Python package that takes a link to a Japanese Syosetu web novel and converts it to an e-reader friendly EPUB file

## Requirements
Requires Python 3
Requires the following pip packages:
```pytz```, ```requests```

## Installation and Usage
Clone this repository and run ```python syosetu2epub.py https://*syosetu.com/******```, replacing the asterisks with your syosetu novel link

It will produce an e-reader friendly, valid EPUB3 document.

## Limitations
Does not yet support image downloading and embedding from syosetu novels.
Does not yet support downloading from a range of chapters, can only download entire Novels.
