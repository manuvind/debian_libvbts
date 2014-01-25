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

import logging
import time
import syslog
import Database

SR = {}

#singleton pattern
def getSubscriberRegistry(db_loc):
    global SR
    if (db_loc not in SR):
        SR[db_loc] = SubscriberRegistry(db_loc)
    return SR[db_loc]

class SubscriberRegistry:

    def __init__(self, db_loc):
        self.db_loc = db_loc
        self.log = logging.getLogger("libvbts.VBTSSubscriberRegistery.SubscriberRegistry")
        self.log.info("Starting: %s" % db_loc)

    def __execute_cmd(self, cmd, args):
        res = None
        finished = False
        while not(finished):
            try:
                res = self.__really_execute_cmd(cmd, args)
                finished = True
            except Database.OperationalError:
                time.sleep(.01)
        return res

    def __really_execute_cmd(self, cmd, args):
        self.log.info(cmd + " " + str(args))
        conn = Database.connect(self.db_loc)
        cur = conn.cursor()
        cur.execute(cmd, args)
        res = cur.fetchone()
        conn.commit()
        if res == None:
            return res
        else:
            return res[0]

    def get(self, to_get, qualifier):
        return self.__get(to_get, qualifier, "SELECT %s FROM sip_buddies WHERE %s=?")

    def get_dialdata(self, to_get, qualifier):
        return self.__get(to_get, qualifier, "SELECT %s FROM dialdata_table WHERE %s=?")

    def get_current_location(self, imsi, fields):
        qstring = "SELECT %s FROM RRLP \
                WHERE name=? order by id desc limit 1" % ",".join(fields)
        return self.__execute_cmd(qstring, (imsi,))

    def __get(self, to_get, qualifier, cmd):
        to_get = to_get.strip()
        qualifier = (qualifier[0].strip(), qualifier[1].strip())
        cmd = cmd % (to_get, qualifier[0])
        args = (qualifier[1],)
        res = self.__execute_cmd(cmd, args)
        return res

    def set(self, to_set, qualifier):
        return self.__set(to_set, qualifier, "UPDATE sip_buddies SET %s=? WHERE %s=?")

    def set_dialdata(self, to_set, qualifier):
        return self.__set(to_set, qualifier, "UPDATE sip_buddies SET %s=? WHERE %s=?")

    def __set(self, to_set, qualifier, cmd):
        to_set = (to_set[0].strip(), to_set[1].strip())
        qualifier = (qualifier[0].strip(), qualifier[1].strip())
        cmd = cmd % (to_set[0], qualifier[0])
        args = (to_set[1],qualifier[1])
        self.__execute_cmd(cmd, args)

    def provision(self, name, number, ip, port):
        res = None
        while not(res):
            try:
                res = self.__provision(name, number, ip, port)
            except Database.OperationalError as e:
                syslog.syslog("VBTS " + str(e))
                time.sleep(.01)
        return res

    def __provision(self, name, number, ip, port):
        try:
            int(number)
            int(port)
        except:
            return False
        insert1_cmd = "INSERT INTO sip_buddies (name, username, type, context, host, callerid, canreinvite, allow, dtmfmode, ipaddr, port, regTime) values (?,?,?,?,?,?,?,?,?,?,?,?)"
        insert1_args = (name, name, "friend", "phones", "dynamic", number, "no", "gsm", "info", ip, port, str(int(time.time())))
        insert2_cmd = "INSERT INTO dialdata_table (exten, dial) values (?, ?)"
        insert2_args = (number, name)
        conn = Database.connect(self.db_loc)
        cur = conn.cursor()
        if (cur.execute("SELECT * FROM sip_buddies WHERE name=?", (name,)).fetchone()):
            return False
        if (cur.execute("SELECT * FROM sip_buddies WHERE callerid=?", (number,)).fetchone()):
            return False
        cur.execute(insert1_cmd, insert1_args)
        cur.execute(insert2_cmd, insert2_args)
        conn.commit()
        return True

    def unprovision(self, name):
        res = None
        while not(res):
            try:
                res = self.__unprovision(name)
            except Database.OperationalError:
                time.sleep(.01)
        return res

    def __unprovision(self, name):
        rm1_cmd = "DELETE FROM sip_buddies WHERE name=?"
        rm2_cmd = "DELETE from dialdata_table WHERE dial=?"
        conn = Database.connect(self.db_loc)
        cur = conn.cursor()
        cur.execute(rm1_cmd, (name,))
        cur.execute(rm2_cmd, (name,))
        conn.commit()
        return True
