# pyfuzz
URL fuzzing tool made of Python

Usage: pyfuzz.py -u http://example.com/en/ -l sharepoint.txt

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -u TARGETURL, --url=TARGETURL
                        Target URL to scan
  -l LISTFILE, --list=LISTFILE
                        List of paths to scan
  -r, --redirect        Show redirect codes (3xx)
