import os
import re
import Config.ConfigServer as Cs
from threading import Thread
from MessageHandler.MsgJudge import judgeAtMe,judgeOneEqualListWord
from MessageHandler.MsgIntf import getAtData
from AiApi.AiModule import AiModule

class FriendMsgHandle:
    def __init__(self, wcf):
        self.wcf = wcf
        configData = Cs.returnConfigData()                
        self.aiSetRole = configData['functionKeyWord']['aiSetRole']
        self.AiApi = AiModule()
        self.msg = {}
        pass

    def TestFriendMsg(self, sender):
        if sender not in self.msg:
            self.msg[sender] = [{"role": "system","content": "你是AI小戴，你无所不能"}]
    
    def MsgHandler(self, message):
        content = message.content.strip()
        sender = message.sender
        msgType = message.type   
        self.TestFriendMsg(sender)
        if msgType == 1:     
            try:
                airesp = self.AiApi.getAi(f"[{sender}问AI小戴]:f{content}",useDeepMode,self.msg[sender])
                if airesp:
                    self.wcf.send_text(msg=f"{airesp}", receiver=sender)
                    return
            except Exception as e:
                print(e)
            self.wcf.send_text(msg=f"小戴睡着了，再问我一次", receiver=sender)
            