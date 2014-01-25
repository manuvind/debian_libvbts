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
from libvbts import FreeSwitchMessenger
from freeswitch import *

def err(msg):
    consoleLog("err", str(msg))
    exit(1)

def parse(args):
    consoleLog('info', "Got Args: " + str(args) + "\n")
    res = args.split("|")
    if (len(res) != 4):
        err("Malformed args")
    return res

def create_user(args):
    (username, target, ip, port) = args
    logging.basicConfig(filename="/tmp/VBTS.log", level="DEBUG")
    fs = FreeSwitchMessenger.FreeSwitchMessenger()
    res = fs.SR_get("callerid", ("name", username))
    if (res):
        return ("You already have a number: " + res)
    if (fs.SR_provision(username, target, ip, port)):
        return ("Your new number is %s" % target)
    else:
        return ("Unable to set number")
    
def chat(message, args):
    res = str(create_user(parse(args)))
    consoleLog('info', res + "\n")
    message.chat_execute('set', '_openbts_ret=%s' % res)
              

def fsapi(session, stream, env, args):
    res = str(create_user(parse(args)))
    consoleLog('info', res + "\n")
    stream.write(res)
    

