# syosetu2epub
Python package that takes a link to a Japanese Syosetu web novel and converts it to an e-reader friendly EPUB file

## Requirements
Requires Python 3
Requires the following pip packages:
```pytz```, ```requests```, ```beautifulsoup4```

## Installation and Usage
Clone this repository and run ```python syosetu2epub.py https://*syosetu.com/******```, replacing the asterisks with your syosetu novel link

It will produce an e-reader friendly, valid EPUB3 document.

## Chapter Range
If you would prefer to download specific chapters, and not the whole novel, add the flag --min # and/or --max #, such as ```python syosetu2epub.py https://*syosetu.com/****** --min 10 --max 50```

## Horizontal Text
Default mode outputs text vertically and flip pages from right to left.
Use the flag ```--horizontal``` in order to read text horizontally and flip pages from left to right.