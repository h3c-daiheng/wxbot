from wcferry import Wcf
from wxlog.log_module import log_info
from threading import Thread
from queue import Empty
from MessageHandler.RoomMsgHandler import RoomMsgHandle


class WxMain(Wcf):
    def __init__(self):
        self.wcf = Wcf()
        self.wcf.enable_receiving_msg()
        self.Rmh = RoomMsgHandle(self.wcf)        
        
    def isLogin(self, ):
        ret = self.wcf.is_login()
        if ret:
            userInfo = self.wcf.get_user_info()
            # 用户信息打印
            print(f"""            
            \t微信名：{userInfo.get('name')}
            \t微信ID：{userInfo.get('wxid')}           
            """.replace(' ', ''))

    def processMsg(self, ):
        # 判断是否登录
        self.isLogin()        
        while self.wcf.is_receiving_msg():
            try:
                msg = self.wcf.get_msg()                
                log_info(f'[*]: 接收到消息\n[*]: 群聊ID: {msg.roomid}\n[*]: 发送人ID: {msg.sender}\n[*]: 发送内容: {msg.content} \n  时间:{msg.ts}--------------------')
                # # 群聊消息处理
                if '@chatroom' in msg.roomid:
                    Thread(target=self.Rmh.mainHandle, args=(msg,)).start()
                # # 好友消息处理
                # elif '@chatroom' not in msg.roomid and 'gh_' not in msg.sender:
                #     Thread(target=self.Fmh.mainHandle, args=(msg,)).start()
                # else:
                #     pass
            except Empty:
                continue



if __name__ == '__main__':
    Ms = WxMain()
    Ms.processMsg()
