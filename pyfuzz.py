#
# pyfuzz v0.1 By Ayoob Ali ( www.AyoobAli.com )
#
import http.client
import sys
import os
import getopt
from optparse import OptionParser
import string

def main():

    parser = OptionParser(usage="%prog -u http://example.com/en/ -l sharepoint.txt", version="%prog 0.1")
    parser.add_option("-u", "--url",   dest="targetURL", help="Target URL to scan")
    parser.add_option("-l", "--list",  dest="listFile",  help="List of paths to scan")
    parser.add_option("-r", "--redirect", action="store_true", dest="showRedirect", help="Show redirect codes (3xx)")
    (options, args) = parser.parse_args()

    if options.listFile == None or options.targetURL == None:
        parser.print_help()
        sys.exit()

    if not os.path.isfile(options.listFile):
        print("Error: File (", options.listFile, ") doesn't exist.")
        sys.exit()

    if options.targetURL[-1] != "/":
        options.targetURL += "/"

    targetPro = ""

    if options.targetURL[:5].lower() == 'https':
        targetDomain = options.targetURL[8:].split("/",1)[0].lower()
        targetPath = "/" + options.targetURL[8:].split("/",1)[1]
        connection = http.client.HTTPSConnection(targetDomain)
        targetPro = "https://"
        print("Target: ", targetPro+targetDomain, "(over HTTPS)")
        print("Path: ", targetPath)
    elif options.targetURL[:5].lower() == 'http:':
        targetDomain = options.targetURL[7:].split("/",1)[0].lower()
        targetPath = "/"+options.targetURL[7:].split("/",1)[1]
        connection = http.client.HTTPConnection(targetDomain)
        targetPro = "http://"
        print("Target set: ", targetDomain)
        print("Path: ", targetPath)
    else:
        targetDomain = options.targetURL.split("/",1)[0].lower()
        targetPath = "/"+options.targetURL.split("/",1)[1]
        connection = http.client.HTTPConnection(targetDomain)
        targetPro = "http://"
        print("Target set: ", targetDomain)
        print("Path: ", targetPath)

    connection.request("HEAD", targetPath+"random/hy27dtwjwysg.txt")
    res = connection.getresponse()

    if res.status == 200:
        print("NOTE: Looks like the server is returning code 200 for all requests, there might be lots of false positive links.")

    if res.status >= 300 and res.status < 400 and options.showRedirect != None:
        print("NOTE: Looks like the server is returning code", res.status, "for all requests, there might be lots of false positive links. try to scan without the option -r")

    tpData = res.read()

    with open(options.listFile) as lFile:
        pathList = lFile.readlines()

    print ("Scanning (",len(pathList),") files...")
    countFound = 0

    for pathLine in pathList:
        pathLine = pathLine.strip("\n")
        pathLine = pathLine.strip("\r")

        if pathLine != "":
            if pathLine[:1] == "/":
                pathLine = pathLine[1:]

            connection.request("GET", targetPath+pathLine)
            res = connection.getresponse()

            if res.status == 200:
                print("Code", res.status,":",targetPro+targetDomain+targetPath+pathLine)
                countFound += 1

            if options.showRedirect != None:
                if res.status >= 300 and res.status < 400:
                    print("Code", res.status,":",targetPro+targetDomain+targetPath+pathLine, "(",res.getheader("location"),")")
                    countFound += 1

            tpData = res.read()

    connection.close()
    print ( "Total Pages found:",countFound )



if __name__ == "__main__":
    main()
