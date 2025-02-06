import os
import re
import Config.ConfigServer as Cs
from threading import Thread
from MessageHandler.MsgJudge import judgeAtMe,judgeOneEqualListWord
from MessageHandler.MsgIntf import getAtData
from AiApi.AiModule import AiModule

aiRole = """
角色：你是AI小戴，你风趣幽默，你专业细致
输出格式：小红书风格
"""


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
            self.msg[sender] = [{"role": "system","content": aiRole}]
    
    def MsgHandler(self, message):
        content = message.content.strip()
        sender = message.sender
        msgType = message.type   
        self.TestFriendMsg(sender)
        useDeepMode=True if "深" in content else False
        if msgType == 1:     
            try:
                airesp = self.AiApi.getAi(f"[{sender}问AI小戴]:f{content}",useDeepMode,self.msg[sender])
                if airesp:
                    self.wcf.send_text(msg=f"{airesp}", receiver=sender)
                    return
            except Exception as e:
                print(e)
            self.wcf.send_text(msg=f"小戴睡着了，再问我一次", receiver=sender)
            
    def mainHandle(self, msg):        
        sender = msg.sender        
        Thread(target=self.MsgHandler, args=(msg,)).start()            