#!/usr/bin/env python3
####
### Project: Pyfuzz
### Version: 1.1.1-Dev.01
### Creator: Ayoob Ali ( www.AyoobAli.com )
### License: MIT
###
from ast import Try
import http.client
import sys
import os
from optparse import OptionParser
import string
import signal
import ssl
from time import sleep
import random
import subprocess
import re

logFile = ""
proxyList = []
proxySelected = 0
proxyUsed = []

def signal_handler(signal, frame):
	print("\nScan stopped by user.")
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def printMSG(printM):
    print(printM)
    if logFile != "":
        fhandle = open(logFile, "a")
        fhandle.write(printM + "\n")
        fhandle.close()

def cmd(command = None):
    returnArr = {}
    returnArr.update({"returnCode": 99})
    try:
        if command == None or command == "":
            return returnArr
        stdout = ""
        stderr = ""
        reCode = subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stData = reCode.communicate()
        returnArr.update({"stdout": stData[0].decode("utf-8")})
        returnArr.update({"stderr": stData[1].decode("utf-8")})
        returnArr.update({"returnCode": reCode.returncode})
        reCode.terminate()
        return returnArr
    except Exception as ErrMs:
        returnArr.update({"error": ErrMs})
        return returnArr

def proxyValidate(proxyServer = None):
    try:
        if proxyServer == None:
            return False
        proxyServer = proxyServer.strip()
        if re.search("^[a-zA-Z0-9\._-]+:[0-9]{1,5}$", proxyServer):
            httpProxy = str(proxyServer).split(':')
            if httpProxy[1].isnumeric() == False or int(httpProxy[1].isnumeric()) < 1 or int(httpProxy[1].isnumeric()) > 65535:
                return False
            return [httpProxy[0], int(httpProxy[1])]
        else:
            return False
    except:
        return False

def selectProxy():
    global proxyList
    global proxySelected
    global proxyUsed
    try:
        if proxyUsed != []:
            proxySelected = proxySelected + 1
        if len(proxyList) == proxySelected:
            proxySelected = 0
        proxyUsed = proxyList[proxySelected]
        return True
    except:
        return False

def setConnection(targetURL = '', reqTimeout = 15, isProxy = False, quite = True):
    global proxyUsed
    targetPro = ""

    if targetURL[:5].lower() == 'https':
        targetDomain = targetURL[8:].split("/",1)[0].lower()
        targetPath = "/" + targetURL[8:].split("/",1)[1]

        if isProxy == True:
            connection = http.client.HTTPSConnection(proxyUsed[0], proxyUsed[1], timeout=reqTimeout, context=ssl._create_unverified_context())
            connection.set_tunnel(targetDomain)
        else:
            connection = http.client.HTTPSConnection(targetDomain, timeout=reqTimeout, context=ssl._create_unverified_context())

        targetPro = "https://"
        if quite == False:
            printMSG("Target       : " + targetPro+targetDomain + " (over HTTPS)")
            printMSG("Path         : " + targetPath)
    elif targetURL[:5].lower() == 'http:':
        targetDomain = targetURL[7:].split("/",1)[0].lower()
        targetPath = "/"+targetURL[7:].split("/",1)[1]
        if isProxy == True:
            connection = http.client.HTTPConnection(proxyUsed[0], proxyUsed[1], timeout=reqTimeout)
            connection.set_tunnel(targetDomain)
        else:
            connection = http.client.HTTPConnection(targetDomain, timeout=reqTimeout)
        targetPro = "http://"
        if quite == False:
            printMSG("Target       : " + targetDomain)
            printMSG("Path         : " + targetPath)
    else:
        targetDomain = targetURL.split("/",1)[0].lower()
        targetPath = "/"+targetURL.split("/",1)[1]
        if isProxy == True:
            connection = http.client.HTTPConnection(proxyUsed[0], proxyUsed[1], timeout=reqTimeout)
            connection.set_tunnel(targetDomain)
        else:
            connection = http.client.HTTPConnection(targetDomain, timeout=reqTimeout)
        targetPro = "http://"
        if quite == False:
            printMSG("Target       : " + targetDomain)
            printMSG("Path         : " + targetPath)
    return [connection, targetDomain, targetPath, targetPro]

def main():
    global logFile
    global proxyList
    global proxyUsed
    parser = OptionParser(usage="%prog -u http://example.com/en/ -l sharepoint.txt", version="%prog 1.1.0")
    parser.add_option("-u", "--url", dest="targetURL", metavar="URL", help="Target URL to scan")
    parser.add_option("-l", "--list", dest="listFile", metavar="FILE", help="List of paths to scan")
    parser.add_option("-r", "--redirect", action="store_true", dest="showRedirect", help="Show redirect codes (3xx)")
    parser.add_option("-e", "--error", action="store_true", dest="showError", help="Show Error codes (5xx)")
    parser.add_option("-s", "--sleep", dest="milliseconds", type="int", metavar="NUMBER", help="Sleep for x milliseconds after each request")
    parser.add_option("-a", "--header", action="append", dest="headers", help="Add Header to the HTTP request (Ex.: -a User-Agent x)", metavar='HEADER VALUE', nargs=2)
    parser.add_option("-b", "--body", dest="requestBody", metavar="Body", help="Request Body (Ex.: name=val&name2=val2)")
    parser.add_option("-x", "--method", dest="requestMethod", metavar="[Method]", help="HTTP Request Method (Ex.: GET, POST, PUT, etc...)")
    parser.add_option("-i", "--ignore", action="append", dest="ignoreText", metavar="Text", help="Ignore results that contain a specific string")
    parser.add_option("-m", "--min-response-size", dest="dataLength", type="int", metavar="NUMBER", help="The minimum response body size in Byte")
    parser.add_option("-g", "--log", dest="logFile", metavar="FILE", help="Log scan results to a file")
    parser.add_option("-f", "--start-from", dest="startFrom", type="int", metavar="NUMBER", help="Start scanning from path number x in the provided list")
    parser.add_option("-t", "--timeout", dest="reqTimeout", type="int", metavar="Seconds", help="Set request timeout")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help="Show error messages")
    parser.add_option("-d", "--define-variable", action="append", dest="variables", help="Define variables to be replaced in URL (Ex.: -d '$varExtension' 'php')", metavar='VARIABLE VALUE', nargs=2)
    parser.add_option("--cmd", dest="excCMD", metavar="Command", help="Execute shell command on each found results (Use with caution). Available variables ({#CODE#}, {#URL#}, {#SIZE#}, {#BODY#}, and {#REDIRECT#})")
    parser.add_option("-p", "--proxy", dest="httpProxy", metavar="PROXY:PORT OR FILE/PATH", help="HTTP Proxy to pass the connection through (Ex.: localhost:9080)")
    parser.add_option("-z", "--randomize-proxy", action="store_true", dest="randomizeProxy", help="Randomize proxy selection for each request (Only while using proxy file)")
   
    startFrom = 0
    reqTimeout = 15

    (options, args) = parser.parse_args()

    if options.requestMethod == None:
        options.requestMethod = "GET"

    if options.requestBody == None:
        options.requestBody = ""

    if options.dataLength == None:
        options.dataLength = 0

    requestHeaders = {}
    if options.headers == None:
        options.headers = []

    for header in options.headers:
        requestHeaders.update({header[0]: header[1]})

    if options.variables == None:
        options.variables = []

    if options.listFile == None or options.targetURL == None:
        parser.print_help()
        sys.exit()

    if options.logFile != None:
        logFile = options.logFile

    if options.startFrom != None:
        startFrom = options.startFrom

    if options.reqTimeout != None:
        if options.reqTimeout > 0:
            reqTimeout = int(options.reqTimeout)

    excCMD = ""
    if options.excCMD != None:
        excCMD = str(options.excCMD)

    isProxy = False
    if options.httpProxy != None:
        isProxy = True
        if os.path.isfile(options.httpProxy):
            with open(options.httpProxy, 'r') as pFile:
                for pLine in pFile.readlines():
                    proxyArr = proxyValidate(pLine)
                    if proxyArr != False and isinstance(proxyArr, list):
                        proxyList.append([proxyArr[0], proxyArr[1]])
            if len(proxyList) == 0:
                printMSG("Error: Proxy file doesn't contain any valid proxy")
                sys.exit()
            random.shuffle(proxyList)
        else:
            proxyArr = proxyValidate(options.httpProxy)
            if proxyArr != False and isinstance(proxyArr, list):
                proxyList.append([proxyArr[0], proxyArr[1]])
            else:
                printMSG("Error: Proxy format should be HOSTNAME:PORT")
                sys.exit()
        selectProxy()

    proxyRand = False
    if options.randomizeProxy != None and isProxy == True:
        proxyRand = True

    if not os.path.isfile(options.listFile):
        printMSG("Error: File (" + options.listFile + ") doesn't exist.")
        sys.exit()

    if options.targetURL[-1] != "/":
        options.targetURL += "/"

    conArr = setConnection(options.targetURL, reqTimeout, isProxy, False)
    connection = conArr[0]
    targetDomain = conArr[1]
    targetPath = conArr[2]
    targetPro = conArr[3]
    
    printMSG("Method       : " + options.requestMethod)
    printMSG("Header       : " + str(requestHeaders))
    printMSG("Body         : " + options.requestBody)
    printMSG("Timeout      : " + str(reqTimeout))
    if isProxy == True:
        printMSG("Proxy        : " + str(proxyUsed[0]) + ":" + str(proxyUsed[1]))

    if options.showRedirect != None:
        printMSG("Show Redirect:  ON")
    if options.showError != None:
        printMSG("Show Error   :  ON")

    try:
        randomPage = ''.join([random.choice(string.ascii_lowercase + string.digits) for n in range(16)])
        connection.request(options.requestMethod, targetPath+randomPage+".txt", options.requestBody, requestHeaders)
        res = connection.getresponse()
    except Exception as ErrMs:
        if options.verbose != None:
            printMSG("MainError: " + str(ErrMs))
        sys.exit(0)

    if res.status == 200:
        printMSG("NOTE: Looks like the server is returning code 200 for all requests, there might be lots of false positive links.")

    if res.status >= 300 and res.status < 400 and options.showRedirect != None:
        printMSG("NOTE: Looks like the server is returning code " + str(res.status) + " for all requests, there might be lots of false positive links. try to scan without the option -r")

    tpData = res.read()

    with open(options.listFile) as lFile:
        pathList = lFile.readlines()
    totalURLs = len(pathList)
    printMSG ("Scanning ( " + str(totalURLs) + " ) files...")
    countFound = 0
    countAll = 0
    strLine = ""
    for pathLine in pathList:
        try:
            countAll = countAll + 1
            pathLine = pathLine.strip("\n")
            pathLine = pathLine.strip("\r")
            if countAll < startFrom:
                continue
            if pathLine != "":
                for variable in options.variables:
                    pathLine = pathLine.replace(variable[0], variable[1])
                if pathLine[:1] == "/":
                    pathLine = pathLine[1:]
                print (' ' * len(strLine), "\r", end="")
                strLine = "Checking ["+str(countAll)+"/"+str(totalURLs)+"] "+targetPath+pathLine
                print (strLine,"\r", end="")
                if options.milliseconds != None:
                    sleep(options.milliseconds/1000)
                connection.request(options.requestMethod, targetPath+pathLine, options.requestBody, requestHeaders)
                res = connection.getresponse()
                resBody = res.read().decode("utf-8")
                resBodySize = len(resBody)
                isignored = False
                if options.ignoreText != None:
                    for igText in options.ignoreText:
                        if igText in resBody:
                            isignored = True

                fURL = str(targetPro+targetDomain+targetPath+pathLine)
                redirectHead = ""
                exCommand = False
                if res.getheader("location") != None:
                    redirectHead = str(res.getheader("location"))
                if res.status >= 200 and res.status < 300:
                    if isignored == False and resBodySize >= options.dataLength:
                        exCommand = True
                        print (' ' * len(strLine), "\r", end="")
                        printMSG("Code " + str(res.status) + " : " + fURL + " (" + str(resBodySize) + " Byte)")
                        countFound += 1

                if options.showError != None:
                    if res.status >= 500 and res.status < 600:
                        if isignored == False and resBodySize >= options.dataLength:
                            exCommand = True
                            print (' ' * len(strLine), "\r", end="")
                            printMSG("Code " + str(res.status) + " : " + fURL)
                            countFound += 1

                if options.showRedirect != None:
                    if res.status >= 300 and res.status < 400:
                        if isignored == False and resBodySize >= options.dataLength:
                            exCommand = True
                            print (' ' * len(strLine), "\r", end="")
                            printMSG("Code " + str(res.status) + " : " + fURL + " ( " + redirectHead + " )")
                            countFound += 1

                if str(excCMD) != "" and exCommand == True:
                    cmdStr = str(excCMD)
                    cmdStr = cmdStr.replace("{#CODE#}", str(res.status))
                    cmdStr = cmdStr.replace("{#URL#}", fURL)
                    cmdStr = cmdStr.replace("{#SIZE#}", str(resBodySize))
                    cmdStr = cmdStr.replace("{#REDIRECT#}", redirectHead)
                    cmdStr = cmdStr.replace("{#BODY#}", resBody)
                    cmdRes = cmd(str(cmdStr))
                    if options.verbose != None and isinstance(cmdRes, dict) and 'stdout' in cmdRes:
                        printMSG(cmdRes['stdout'])
            if proxyRand == True:
                selectProxy()
                conArr = setConnection(options.targetURL, reqTimeout, isProxy, True)
                connection = conArr[0]
                targetDomain = conArr[1]
                targetPath = conArr[2]
                targetPro = conArr[3]

        except Exception as ErrMs:
            if options.verbose != None:
                print (' ' * len(strLine), "\r", end="")
                printMSG("Error[" + str(countAll) + "]: " + str(ErrMs))
            try:
                connection.close()
                if proxyRand == True:
                    selectProxy()
                    conArr = setConnection(options.targetURL, reqTimeout, isProxy, True)
                    connection = conArr[0]
                    targetDomain = conArr[1]
                    targetPath = conArr[2]
                    targetPro = conArr[3]
                pass
            except Exception as e:
                if options.verbose != None:
                    printMSG("Error2:" + str(e))
                pass
        
    connection.close()
    print (' ' * len(strLine), "\r", end="")
    printMSG( "Total Pages found: " + str(countFound) )



if __name__ == "__main__":
    main()
