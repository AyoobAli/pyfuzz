# pyfuzz v0.50
URL fuzzing tool made of Python.

This tool needs Python v3.

-------
I built this tool while doing a pentent on a sharepoint website, I needed something to do the fuzzing to find some pages in the server.
Similar tool is [DirBuster](https://www.owasp.org/index.php/Category:OWASP_DirBuster_Project) from OWASP, but this is a command line.


Usage:-

python3 pyfuzz.py -u http://example.com/en/ -l sharepoint.txt

OR

./pyfuzz -u http://example.com/en/ -l sharepoint.txt

-------

# Change LOG

[24-07-2018] v0.5.1

   - [Added] Option to ignore results that contain a specific string in the response body.

[23-07-2018] v0.5.0

   - [Added] Option to add Custom Header to the request (-a).
   - [Added] Option to Change the HTTP Request Method (-x).
   - [Added] Option to add a Request Body (-b).
   - [Fixed] First random page to check response code now randomly generated.
   - [Fixed] Minor issue.


# TO-DO:

   - Add the ability to filter results based on a string in the response body.