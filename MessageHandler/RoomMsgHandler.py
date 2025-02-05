import os
import re
import Config.ConfigServer as Cs
from threading import Thread
from MessageHandler.MsgJudge import judgeAtMe,judgeOneEqualListWord
from MessageHandler.MsgIntf import getAtData
from AiApi.AiModule import AiModule

class RoomMsgHandle:
    def __init__(self, wcf):
        self.wcf = wcf
        configData = Cs.returnConfigData()        
        self.joinRoomMsg = configData['customMsg']['joinRoomMsg']     
        self.aiPicKeyWords = configData['functionKeyWord']['aiPic']
        self.AiApi = AiModule()
        pass
    
    def JoinRoomWelcome(self, msg):
        """
        进群欢迎
        :param msg:
        :return:
        """
        try:
            ret = 1
            appoint = 1
            content = msg.content.strip()
            wx_names = None
            if '二维码' in content:
                wx_names = re.search(r'"(?P<wx_names>.*?)"通过扫描', content)
            elif '邀请' in content:
                wx_names = re.search(r'邀请"(?P<wx_names>.*?)"加入了', content)
            if wx_names:
                wx_names = wx_names.group('wx_names')
                if '、' in wx_names:
                    wx_names = wx_names.split('、')
                else:
                    wx_names = [wx_names]
            for wx_name in wx_names:
                joinRoomMsg = f'@{wx_name} ' + self.joinRoomMsg.replace("\\n", "\n")
                self.wcf.send_text(msg=joinRoomMsg, receiver=msg.roomid)
        except Exception as e:
            pass
    
    def judgeAtMe(selfId, content, atUserList):
        """
        判断有人@我, @所有人不算
        :param selfId:
        :param atUserList:
        :return:
        """
        if selfId in atUserList and '所有人' not in content:
            return True
        return False


    def MsgHandler(self, message):   
        content = message.content.strip()
        sender = message.sender
        roomId = message.roomid
        msgType = message.type
        #senderName = self.wcf.get_alias_in_chatroom(sender, roomId)
        atUserLists, noAtMsg = getAtData(self.wcf, message)
                         
        if judgeAtMe(self.wcf.self_wxid, content, atUserLists) and not judgeOneEqualListWord(noAtMsg, self.aiPicKeyWords):
            useDeepMode=True if "深" in noAtMsg else False
            if useDeepMode:
                self.wcf.send_text(msg=f"@{sender}:使用深度分析模型，请稍后", receiver=roomId)
            try:
                airesp = self.AiApi.getAi(f"[{sender}问AI小戴]:f{noAtMsg}",useDeepMode)
                if airesp:
                    self.wcf.send_text(msg=f"@{sender}:{airesp}", receiver=roomId)
                    return
            except Exception as e:
                print(e)
            self.wcf.send_text(msg=f"@{sender}:小戴睡着了，再问我一次，或者找小贝壳", receiver=roomId)
            return 
        
    def mainHandle(self, msg):
        roomId = msg.roomid
        sender = msg.sender
        Thread(target=self.JoinRoomWelcome, args=(msg,)).start()
        Thread(target=self.MsgHandler, args=(msg,)).start()
    
if __name__ == '__main__':
    pass    