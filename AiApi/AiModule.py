import Config.ConfigServer as ConfigServer
from openai import OpenAI
from wxlog.log_module import log_info as log_info
import time
import json


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



class AiModule():
    def __init__(self):
        self.configData = ConfigServer.returnConfigData()
        #self.systemmsg = self.configData['aiConfig']['systemAiRule']
        self.aiList = self.configData['AiInterface']['AiList']      
        self.msglength = self.configData['aiConfig']['msglength']
        print(self.msglength)
        self.msg = [{
            "role": "system",
            "content": AiSystemMsg
        }]
        
    def dump_msg(self,messages):
        for msg in messages:
            print(msg)
            
    def get_deep_seek_api_retry(self, ainame, messages, useDeepMode,tools=None, RetryCnt=2):  
        self.dump_msg(messages)
        baseurl = self.configData['AiInterface'][ainame]['url']  
        apikey = self.configData['AiInterface'][ainame]['key']  
        module = self.configData['AiInterface'][ainame]['modulename']          
        if useDeepMode and self.configData['AiInterface'][ainame]['deepmodule']:
            module = self.configData['AiInterface'][ainame]['deepmodule']

        print(baseurl,apikey,module)
        max_tokens = 1024
        # if self.configData['AiInterface'][module].get('MaxToken'):
        #     max_tokens = self.configData['AiInterface']['module'].get('MaxToken')
        
        for cnt in range(RetryCnt):           
            Client = OpenAI(api_key=apikey, base_url=baseurl)            
            try:
                if tools:
                    response = Client.chat.completions.create(
                        model=module,
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                        max_tokens=max_tokens                       
                    )
                else:
                    response = Client.chat.completions.create(
                        model=module,
                        messages=messages,
                        max_tokens=max_tokens                            
                    )
                return response
            except Exception as e:
                log_info(f'[-]: deepSeek conversation interface error, retrying {cnt}... {e}')
                # Delay 3 seconds
                time.sleep(3)
        return None

    def getAi(self,content,useDeepMode):       
        self.msg.append({
            "role": "user",
            "content": content
        })
        for ainame in self.aiList:
            try:                
                resp = self.get_deep_seek_api_retry(ainame, self.msg , useDeepMode)       
                assistant_content = resp.choices[0].message.content
                self.msg.append({"role": "assistant", "content": f"{assistant_content}"})
                if len(self.msg) == self.msglength:
                    del self.msg[1:2] # 删除第一个用户输入              
                print(assistant_content)                
                return assistant_content
            except Exception as e:
                print(f'[-]: Error in getAi method: {e}')
                log_info(f'[-]: Error in getAi method: {e}')
        return None

if __name__ == '__main__':
    Ai = AiModule()
    print(Ai.getAi('你好','deepseek-ai/DeepSeek-V3'))
