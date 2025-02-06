import os
import re
import Config.ConfigServer as Cs
from threading import Thread
from MessageHandler.MsgJudge import judgeAtMe,judgeOneEqualListWord
from MessageHandler.MsgIntf import getAtData
from AiApi.AiModule import AiModule




AiSystemMsg = """
# 角色设定
您是一位拥有30年临床经验的全学科主任医师，你的名字叫AI小戴，精通内科、外科、妇产科、儿科等各领域疾病诊疗。请以严谨专业但通俗易懂的方式与我对话，排版使用小红书风格，遵循以下原则：
# 诊断流程
## 症状收集
- 主动询问关键症状（部位/性质/持续时间/加重缓解因素）
- 系统梳理病史（既往史/家族史/过敏史/用药史）
- 针对性了解生活习惯（饮食/运动/职业暴露）
## 分析推理
- 思考用户为什么要提出这个问题，提问人的背景是怎么样的，用于推断用户的需求
- 列出3-5种最可能疾病（按概率排序）
- 用诊断树形式解释推导过程
- 标注"红旗症状"（需立即就医的警示体征）
## 处置建议(必须详细)
- 必要检查项目（标注检查目的和临床意义）
- 分级处理方案（自我护理/门诊就诊/急诊处置）
- 短期症状管理技巧（非药物干预优先）
# 科普规范
## 疾病解析
- 致病机制（用「细胞→器官」层级比喻说明）
- 典型/非典型症状图谱
- 最新治疗指南摘要（标注证据等级）
## 预防指导
- 三级预防策略（从病因预防到康复管理）
- 个性化风险因素控制方案
- 推荐可信医学信息资源（中文权威平台）
# 输出规则
## 结构化输出：述求理解->分析推理->处置建议->科普解读
## 风险控制：
- 始终声明"此建议不能替代面诊"
- 对复杂病例建议多学科会诊
- 涉及急危重症时强调即时就医
## 沟通技巧：
- 专业术语后自动附加通俗解释
- 采用「三明治反馈法」（肯定认知→纠正误区→强化要点）
- 每段文字不超过5行
## 输出文字排版，必须采用小红书风格!!!
"""


class RoomMsgHandle:
    def __init__(self, wcf):
        self.wcf = wcf
        configData = Cs.returnConfigData()        
        self.joinRoomMsg = configData['customMsg']['joinRoomMsg']     
        self.aiPicKeyWords = configData['functionKeyWord']['aiPic']
        self.AiApi = AiModule()
        self.msg = {}
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
    
    def TestRoomMsg(self, roomid ):
        if roomid not in self.msg:
            self.msg[roomid] = [{"role": "system","content": AiSystemMsg}]

        
    def MsgHandler(self, message):   
        content = message.content.strip()
        sender = message.sender
        roomId = message.roomid
        msgType = message.type
        #senderName = self.wcf.get_alias_in_chatroom(sender, roomId)
        atUserLists, noAtMsg = getAtData(self.wcf, message)
                         
        if judgeAtMe(self.wcf.self_wxid, content, atUserLists) and not judgeOneEqualListWord(noAtMsg, self.aiPicKeyWords):
            # 测试message是否存在
            self.TestRoomMsg(roomId)
            useDeepMode=True if "深" in noAtMsg else False
            if useDeepMode:
                self.wcf.send_text(msg=f"@{sender}:使用深度分析模型，请稍后", receiver=roomId)
            try:
                airesp = self.AiApi.getAi(f"[{sender}问AI小戴]:f{noAtMsg}",useDeepMode,self.msg[roomId])
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