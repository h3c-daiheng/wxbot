from wxlog.log_module import log_info
import xml.etree.ElementTree as ET

def getAtData(wcf, msg):
    """
    处理@信息
    :param msg:
    :param wcf:
    :return:
    """
    noAtMsg = msg.content
    try:
        root_xml = ET.fromstring(msg.xml)
        atUserListsElement = root_xml.find('.//atuserlist')
        atUserLists = atUserListsElement.text.replace(' ', '').strip().strip(',').split(
            ',') if atUserListsElement is not None else None
        if not atUserLists:
            return '', ''
        atNames = []
        for atUser in atUserLists:
            atUserName = wcf.get_alias_in_chatroom(atUser, msg.roomid)
            atNames.append(atUserName)
        for atName in atNames:
            noAtMsg = noAtMsg.replace('@' + atName, '')
    except Exception as e:
        log_info(f'[~]: 处理@消息出现小问题, 仅方便开发调试, 不用管此报错: {e}')
        return '', ''
    return atUserLists, noAtMsg.strip()