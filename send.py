#!/usr/bin/python
'''
Created on Aug 2, 2017

@author: Tyler Thompson
'''

import optparse,sys
from Classes import Tools,Computers

#configFilePath = "/archive/scripts/C-220.json"
configFilePath = "/alva/LabInfo/json/C-220.json"

tools = Tools.Tools()
cd = Computers.Computers(configFilePath=configFilePath)

def main():
    args = getArgs()
    #print "DEBUG ARGS: " + str(args)

    if args.p == True:
        tools.prettyPrintObjects(objects=cd.computers, title="C-220 Computers")
        sys.exit(0)
    if args.c == None:
        print "You must pass a command. Use --help to see usage."
        sys.exit(0)

    #limit list of computers to that specified
    cd.setRange(idRange=args.n)
    cd.setList(idList=args.m)

    confirmSend(cmd=args.c)

    cd.sendSshToAll(cmd=args.c, user=args.u)


def confirmSend(cmd):
    yesCmd = "yeah bro"
    noCmd = "nah man"
    print "\nPreparing to send terminal command '" + cmd + "' to the following computers:"
    tools.prettyPrintObjects(objects=cd.computers, title="Targeted Computers")
    while True:
        userInput = raw_input("Are you sure you want to send the command? [ " + yesCmd + " | " + noCmd + " ]\n>> ")
        if userInput != yesCmd and userInput != noCmd:
            print "Please specify '" + yesCmd + "' or '" + noCmd + "'"
        if userInput == noCmd:
            print "Thats cool..."
            sys.exit(0)
        if userInput == yesCmd:
            print "Hell yeah, lets do this!"
            break



def getArgs():
    parser = optparse.OptionParser(usage='%prog -c <COMMAND> [options]',description="C-220 SSH Send. Send a terminal command to all the computers in C-220. Optionally you can send a command to a single computer or a range of computers.")
    parser.add_option('-c', action='store', help="Command to send")
    parser.add_option('-u', action='store', default="root", help="User to send command as. Default: root")
    parser.add_option('-i', action='store', default="~/.ssh/id_rsa", help="Identity file to use. Default: ~/.ssh/id_rsa")
    parser.add_option('-n', action="store", default=False, help="Set a range of computers to send command to. ie. 00-06")
    parser.add_option('-m', action="store", default=False, help="Set comma delimited list of computers to send command to. ie. 03,05,10,23")
    parser.add_option('-p', action="store_true", default=False, help="Print the config and exit.")
    options, args = parser.parse_args()
    return options


if __name__ == '__main__':
    main()