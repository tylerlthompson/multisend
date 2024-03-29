'''
Created on Aug 2, 2017

@author: Tyler Thompson
'''

import json,re,sys,time
from Objects import Computer
from Classes import Tools, SshSendThreaded, RsyncThreaded

class Computers(object):
    '''
    classdocs
    '''


    def __init__(self, configFilePath):
        '''
        Constructor
        '''
        self.tools = Tools.Tools()
        self.configFilePath = configFilePath
        try:
            self.computers = self.getComputers(printConfig=False)
        except:
            print "Failed to read file: " + str(self.configFilePath)
            sys.exit(0)

    def getComputers(self, printConfig=True):
        computers = []
        with open(self.configFilePath) as configFile:
            labInfo = json.load(configFile)
        for id, info in labInfo.iteritems():
            newComputer = Computer.Computer(id=id, hostname=info['hostname'], mac=info['mac'], ip=info['ip'],
                                            assettag=info['assettag'])
            computers.append(newComputer)
        computers.sort(key=lambda x: x.id)
        if printConfig:
            self.tools.prettyPrintObjects(objects=computers, title="C-220 Computers")
        return computers

    def setRange(self, idRange):
        if idRange == False:
            return
        idRangeList = idRange.split('-')
        start = int(idRangeList[0])
        stop = int(idRangeList[1]) + 1
        comLength = len(self.computers)
        if stop > comLength:
            stop = comLength
        setComputers = []
        for i in range(start, stop):
            computer = self.computers[i]
            cid = int(re.sub('[^0-9]','', computer.id))
            if cid == i:
                setComputers.append(computer)
        self.computers = setComputers

    def setList(self, idList):
        if idList == False:
            return
        ids = idList.split(',')
        setComputers = []
        for computer in self.computers:
            for i in range(len(ids)):
                cid = int(re.sub('[^0-9]','', computer.id))
                if cid == int(ids[i]):
                    setComputers.append(computer)
        self.computers = setComputers

    # def sendSshToAll(self, cmd, user, idFile, dfstatus=False):
    #     print "Sending ssh command '" + cmd + "' to targeted computers..."
    #     sshSendStatuses = []
    #     for computer in self.computers:
    #         print computer.hostname + "... ",
    #         ping = self.tools.getPing(ip=computer.ip)
    #         newStatus = SendStatus.SendStatus(id=computer.id, ip=computer.ip, user=user, ping=ping)
    #         if ping == True:
    #             newStatus.functionReturn = self.tools.sendSsh(user=user, ip=computer.ip, cmd=cmd, idFile=idFile)
    #
    #             #detect if reading a deep freeze status report
    #             if dfstatus == True:
    #                 if "BOOT FROZEN" in newStatus.functionReturn:
    #                     newStatus.functionReturn = "FROZEN"
    #                 elif "BOOT THAWED" in newStatus.functionReturn:
    #                     newStatus.functionReturn = "THAWED"
    #                 else:
    #                     newStatus.functionReturn = "UNKNOWN"
    #
    #             if "timed out" in newStatus.functionReturn:
    #                 print "Connection timed out."
    #             else:
    #                 print "Sent."
    #         elif ping == False:
    #             print "Ping failed for " + computer.id + ", " + computer.ip + " Skipping..."
    #         sshSendStatuses.append(newStatus)
    #
    #
    #     self.tools.prettyPrintObjects(objects=sshSendStatuses, title="SSH Send Report")
    #     return sshSendStatuses

    def sendSshToAllThreaded(self, cmd, user, idFile, dfstatus=False, rename=False):
        print "Sending ssh command '" + cmd + "' to targeted computers...",

        #create thread object for each computer
        threads = []
        for computer in self.computers:
            #print computer.hostname + "... ",
            if rename == True:
                computer.cmd = str(cmd) + str(computer.hostname) + " && hostname"
            else:
                computer.cmd = cmd
            computer.idFile = idFile
            computer.user = user
            computer.dfstatus = dfstatus
            threads.append(SshSendThreaded.SshSendThreaded(computer=computer))

        self.executeThreads(threads=threads)

        #print the report
        self.tools.prettyPrintObjects(objects=self.computers, title="SSH Send Report", objFilter="src,cmd,dest,idFile,dfstatus,user")

    # def sendFileToAll(self, src, dest, user, idfile):
    #     print "Sending file: " + src + " to: " + dest + " on targeted computers..."
    #     fileSendStatuses = []
    #     for computer in self.computers:
    #         print computer.hostname + "... ",
    #         ping = self.tools.getPing(ip=computer.ip)
    #         newStatus = SendStatus.SendStatus(id=computer.id, ip=computer.ip, user=user, ping=ping)
    #         if ping == True:
    #             newStatus.functionReturn = self.tools.sendFile(user=user, ip=computer.ip, src=src, dest=dest, idFile=idfile)
    #             if newStatus.functionReturn != "File transfer complete":
    #                 print newStatus.functionReturn
    #             else:
    #                 print "Sent."
    #         elif ping == False:
    #             print "Ping failed for " + computer.id + ", " + computer.ip + " Skipping..."
    #         fileSendStatuses.append(newStatus)
    #
    #     self.tools.prettyPrintObjects(objects=fileSendStatuses, title="RSYNC File Send Report")
    #     return fileSendStatuses

    def sendFileToAllThreaded(self, src, dest, user, idfile):
        print "Sending file: " + src + " to: " + dest + " on targeted computers...",

        #create all threads
        threads = []
        for computer in self.computers:
            computer.src = src
            computer.dest = dest
            computer.user = user
            computer.idFile = idfile
            threads.append(RsyncThreaded.RsyncThreaded(computer=computer))

        self.executeThreads(threads=threads)

        # print the report
        self.tools.prettyPrintObjects(objects=self.computers, title="RSYNC File Send Report", objFilter="cmd,idFile,dfstatus,user")

    def executeThreads(self, threads):
        # start all threads
        for thread in threads:
            #print ("."),
            sys.stdout.write('.')
            sys.stdout.flush()
            thread.start()

        print "Done.\nWaiting for threads to terminate...",
        # wait for all threads to terminate
        while True:
            time.sleep(0.2)
            exit = True
            for thread in threads:
                if thread.isAlive() == True:
                    exit = False
            sys.stdout.write('.')
            sys.stdout.flush()
            if exit == True:
                break
        print "Done."
        # join all the threads
        for thread in threads:
            thread.join()
