#!/usr/bin/env python3
# coding: utf-8

from wxpy import *
from config import *
import re
from wxpy.utils import start_new_thread
import time
import os

'''
使用 cache 来缓存登陆信息，同时使用控制台登陆
'''
bot = Bot('bot.pkl', console_qr=True)
bot.messages.max_history = 0

'''
开启 PUID 用于后续的控制
'''
bot.enable_puid('wxpy_puid.pkl')

'''
所有消息控制台输出开关
'''
msg_print = True

'''
邀请信息处理
'''
rp_new_member_name = (
    re.compile(r'^"(.+)"通过'),
    re.compile(r'邀请"(.+)"加入'),
    re.compile(r'invinted "(.+)" to the group chat'),
)

# 格式化 Group
try:
    groups = [bot.groups().search(puid=x)[0] for x in group_puids]
    groups.extend([bot.groups().search(x)[0] for x in group_fullnames])
except:
    print("查找管理群出错！请检查管理群 puid 是否输入正确")
    quit()

# 格式化 Admin
try:
    admins = [bot.friends().search(puid=x)[0] for x in admin_puids]
    if not bot.self in admins:
        admins.append(bot.self)
except:
    print("查找管理员出错！请检查管理员 puid 是否输入正确")
    quit()

# 私聊开关
user_in_chat = []

# 远程踢人命令: 移出 @<需要被移出的人>
rp_kick = re.compile(r'^(?:移出|移除|踢出|拉黑)\s*@(.+?)(?:\u2005?\s*$)')

# 图灵机器人设定
tuling = Tuling(api_key=turing_key) if turing_key else None

# 下方为函数定义

def get_time():
    return str(time.strftime("%Y-%m-%d %H:%M:%S"))

'''
机器人消息提醒设置
'''
alert_receiver = None
if alert_user:
    try:
        alert_receiver = ensure_one(bot.friends().search(alert_user))
    except:
        print("警报用户设置有误，请检查群名是否存在且唯一")
elif alert_group:
    try:
        alert_receiver = ensure_one(bot.groups().search(alert_group))
    except:
        print("警报群设置有误，请检查群名是否存在且唯一")
if alert_receiver is None:
    alert_receiver = bot.self
logger = get_wechat_logger(alert_receiver, level=alert_level)
logger.error(str("机器人登陆成功！"+ get_time()))

'''
重启机器人
'''
def _restart():
    os.execv(sys.executable, [sys.executable] + sys.argv)

'''
状态汇报
'''
def status():
    status_text = "{} 机器人目前在线，共有好友 【{}】 群 【{}】".format(get_time(), str(len(bot.friends())), str(len(bot.groups()))) + '\n' + "管理员 【{}】 管理群 【{}】 聊天在线 【{}】".format(str(len(admins)), str(len(groups)), str(len(user_in_chat)))
    return status_text

'''
定时报告进程状态
'''
def heartbeat():
    while bot.alive:
        time.sleep(3600)
        # noinspection PyBroadException
        try:
            logger.error(status())
        except ResponseError as e:
            if 1100 <= e.err_code <= 1102:
                logger.critical('LCBot offline: {}'.format(e))
                _restart()

start_new_thread(heartbeat)

'''
判断消息发送者是否在管理员列表
'''
def from_admin(msg):
    """
    判断 msg 中的发送用户是否为管理员
    :param msg:
    :return:
    """
    if not isinstance(msg, Message):
        raise TypeError('expected Message, got {}'.format(type(msg)))
    from_user = msg.member if isinstance(msg.chat, Group) else msg.sender
    return from_user in admins

'''
远程踢人命令
'''
def remote_kick(msg):
    if msg.type is TEXT:
        match = rp_kick.search(msg.text)
        if match:
            name_to_kick = match.group(1)

            if not from_admin(msg) and not silence_mode:
                return '感觉有点不对劲… @{}'.format(msg.member.name)

            member_to_kick = ensure_one(list(filter(
                lambda x: x.name == name_to_kick, msg.chat)))
            if member_to_kick  == bot.self:
                return '无法移出 @{}'.format(member_to_kick.name)
            if member_to_kick in admins:
                return '无法移出 @{}'.format(member_to_kick.name)

            logger.error(get_time() + str(" 【"+member_to_kick.name + "】 被 【"+msg.member.name+"】 移出 【" + msg.sender.name+"】"))
            if member_to_kick in msg.sender:
                member_to_kick.remove()
                kick_info = '成功移出 @{}'.format(member_to_kick.name)
            else:
                kick_info = '@{} 已不在群中'.format(member_to_kick.name)

            for ready_to_kick_group in  groups:
                if member_to_kick in ready_to_kick_group:
                    ready_to_kick_group.remove_members(member_to_kick)
                    logger.error(get_time()+ str("【"+member_to_kick.name + "】 被系统自动移出 " +  ready_to_kick_group.name))

            return kick_info


'''
邀请消息处理
'''
def get_new_member_name(msg):
    # itchat 1.2.32 版本未格式化群中的 Note 消息
    from itchat.utils import msg_formatter
    msg_formatter(msg.raw, 'Text')

    for rp in rp_new_member_name:
        match = rp.search(msg.text)
        if match:
            return match.group(1)

'''
定义邀请用户的方法。
按关键字搜索相应的群，如果存在相应的群，就向用户发起邀请。
'''
def invite(user, keyword):
    from random import randrange
    group = bot.groups().search(keyword_of_group[keyword])
    if len(group) > 0:
        for i in range(0, len(group)):
            if user in group[i]:
                content = "您已经加入了 {} [微笑]".format(group[i].nick_name)
                user.send(content)
                return
        if len(group) == 1:
            target_group = group[0]
        else:
            index = randrange(len(group))
            target_group = group[index]
        try:
            target_group.add_members(user, use_invitation=True)
        except:
            user.send("邀请错误！机器人邀请好友进群已达当日限制。请您明日再试")
    else:
        user.send("该群状态有误，您换个关键词试试？")

# 下方为消息处理

'''
所有消息注册函数
控制台打印消息记录
'''
@bot.register()
def common_process(msg):
    if msg_print:
        print(msg)

'''
处理加好友请求信息。
如果验证信息文本是字典的键值之一，则尝试拉群。
'''
@bot.register(msg_types=FRIENDS)
def new_friends(msg):
    common_process(msg)
    if msg.text.lower() in keyword_of_group.keys():
        user = msg.card.accept()
        user.send(invite_text)
        invite(user, msg.text.lower())

@bot.register(Friend, msg_types=TEXT)
def exist_friends(msg):
    common_process(msg)
    if msg.text.lower() in ["help", "帮助"]:
        msg.sender.send(help_text)
    elif msg.text.lower() in keyword_of_group.keys():
        invite(msg.sender, msg.text.lower())
    else:
        if msg.sender in user_in_chat:
            if msg.text == user_chat_off_text:
                user_in_chat.remove(msg.sender)
                return user_chat_off_reply
            elif turing_key:
                tuling.do_reply(msg)
            else:
                return invite_text
        else:
            if msg.text.lower() == user_chat_on_text:
                user_in_chat.append(msg.sender)
                return user_chat_on_reply

# 管理群内的消息处理
@bot.register(groups, except_self=False)
def wxpy_group(msg):
    common_process(msg)
    ret_msg = remote_kick(msg)
    if ret_msg:
        return ret_msg
    elif msg.is_at and not silence_mode:
        if turing_key :
            tuling.do_reply(msg)
        else:
            return "忙着呢，别烦我！";

@bot.register(groups, NOTE)
def welcome(msg):
    common_process(msg)
    name = get_new_member_name(msg)
    if name and not silence_mode:
        return welcome_text.format(name)

@bot.register([bot.self, bot.file_helper, alert_receiver], except_self=False)
def alert_command(msg):
    if from_admin(msg):
        if msg.text == "#status":
            return status()
        elif msg.text == "#restart":
            _restart()
        else:
            return exist_friends(msg)

embed()
