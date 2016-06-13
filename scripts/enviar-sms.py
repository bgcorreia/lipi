#!/usr/bin/env python

import gammu
import sys

print sys.argv[1]
print sys.argv[2]

sm = gammu.StateMachine()
sm.ReadConfig()
sm.Init()
message = {
'Text': sys.argv[1],
'SMSC': {'Location': 1},
'Number': sys.argv[2],
}
sm.SendSMS(message)
