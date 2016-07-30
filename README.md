# pyfuzz
URL fuzzing tool made of Python.

This tool needs Python v3.

-------
I built this tool while doing a pentent on a sharepoint website, I needed something to do the fuzzing and find some pages in the server.
Similar tool is [DirBuster](https://www.owasp.org/index.php/Category:OWASP_DirBuster_Project) from OWASP (Also better), but this is a command line.


Usage:-

python3 pyfuzz.py -u http://example.com/en/ -l sharepoint.txt

OR

./pyfuzz -u http://example.com/en/ -l sharepoint.txt

