import Config.ConfigServer as ConfigServer
from openai import OpenAI
from wxlog.log_module import log_info as log_info
import time
import json




class AiModule():
    def __init__(self):
        self.configData = ConfigServer.returnConfigData()
        #self.systemmsg = self.configData['aiConfig']['systemAiRule']
        self.aiList = self.configData['AiInterface']['AiList']      
        self.MsgMaxDeepDepth = self.configData['aiConfig']['msglength']

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

    def getAi(self,content,useDeepMode,messages:list):
        messages.append({"role": "user", "content": content})
        for ainame in self.aiList:
            try:                
                resp = self.get_deep_seek_api_retry(ainame, messages , useDeepMode)       
                assistant_content = resp.choices[0].message.content
                messages.append({"role": "assistant", "content": f"{assistant_content}"})
                if len(messages) == self.MsgMaxDeepDepth:
                    del messages[1:2] # 删除第一个用户输入                                            
                return assistant_content
            except Exception as e:
                print(f'[-]: Error in getAi method: {e}')
                log_info(f'[-]: Error in getAi method: {e}')
        return None

if __name__ == '__main__':
    Ai = AiModule()
    print(Ai.getAi('你好','deepseek-ai/DeepSeek-V3'))
