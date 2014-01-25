#Copyright 2011 Kurtis Heimerl <kheimerl@cs.berkeley.edu>. All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification, are
#permitted provided that the following conditions are met:
#
#   1. Redistributions of source code must retain the above copyright notice, this list of
#      conditions and the following disclaimer.
#
#   2. Redistributions in binary form must reproduce the above copyright notice, this list
#      of conditions and the following disclaimer in the documentation and/or other materials
#      provided with the distribution.
#
#THIS SOFTWARE IS PROVIDED BY Kurtis Heimerl ''AS IS'' AND ANY EXPRESS OR IMPLIED
#WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
#FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Kurtis Heimerl OR
#CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#The views and conclusions contained in the software and documentation are those of the
#authors and should not be interpreted as representing official policies, either expressed
#or implied, of Kurtis Heimerl.

import Database
import logging

con = {}

#singleton pattern
def getConfig(db_loc):
    global con
    if (db_loc not in con):
        con[db_loc] = Configuration(db_loc)
    return con[db_loc]

class Configuration:

    def __init__(self, db_loc):
        #hack around some weird threading issues. We can't load it here. 
        self.db_loc = db_loc
        self.log = logging.getLogger("libvbts.VBTSConfiguration.Configuration")

    def __execute_cmd(self, cmd):
        conn = Database.connect(self.db_loc)
        cur = conn.cursor()
        cur.execute(cmd)
        res = cur.fetchone()
        return res
    
    def getField(self, field):
        cmd = "SELECT VALUESTRING from CONFIG WHERE KEYSTRING='%s'" % field
        res = self.__execute_cmd(cmd)
        if (res):
            return res[0]
        else:
            raise Exception("Field %s not found" % field)

if __name__ == '__main__':
    import sys
    if (len(sys.argv) < 3):
        print ("Usage:")
        print ("VBTS_Configuration DB_LOC KEYSTRING")
    c = Configuration(sys.argv[1])
    print(c.getField(sys.argv[2]))
         
