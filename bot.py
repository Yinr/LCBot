#!/usr/bin/env python3
# coding: utf-8

from wxpy import *
from config import *
import re
from wxpy.utils import start_new_thread
import time
import os
import platform

'''
使用 cache 来缓存登陆信息，同时使用控制台登陆
'''
console_qr = (False if platform.system() == 'Windows' else True)
bot = Bot('bot.pkl', console_qr=console_qr)
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
    re.compile(r'^"((\n?.?)+)"通过'),
    re.compile(r'邀请"((\n?.?)+)"加入'),
    re.compile(r'invited "((\n?.?)+)" to the group chat'),
)


def fresh_groups():
    '''
    管理员群及被管理群初始化
    '''
    global groups, admin_group
    # 格式化被管理群 Groups
    try:
        allgroups = bot.groups(update=True)
        groups = list(
            filter(lambda x: x.name.startswith(group_prefix),
                   allgroups.search(group_prefix)))
        groups += list(
            filter(lambda x: x.name in additional_groups, allgroups))
    except:
        print("查找被管理群出错！请检查被管理群前缀（group_prefix）是否配置正确")
        quit()

    # 格式化管理员群 Admin_group
    try:
        admin_group = ensure_one(
            bot.groups(update=True).search(admin_group_name))
    except:
        print("查找管理员群出错！请检查管理群群名（admin_group_name）是否配置正确")
        print("现将默认设置为只有本帐号为管理员")
        admin_group = None

fresh_groups()

# 私聊开关
user_in_chat = []

# 远程踢人命令: 移出 @<需要被移出的人>
rp_kick = re.compile(r'^(?:移出|移除|踢出|拉黑)\s*@((\n?.?)+?)(?:\u2005?\s*$)')

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
logger = get_wechat_logger(alert_receiver, level=alert_level)
logger.error(str("机器人登陆成功！" + get_time()))


def random_sleep():
    '''
    随机延时
    '''
    from random import randrange
    rnd_time = randrange(2, 7)
    time.sleep(rnd_time)


def _restart():
    '''
    重启机器人
    '''
    os.execv(sys.executable, [sys.executable] + sys.argv)


def status():
    '''
    状态汇报
    '''
    status_text = get_time() + " 机器人目前在线，共有好友 【" + str(len(bot.friends())) + "】 群 【" + str(len(bot.groups())) + "】\n管理员 【" + str(len(admins)) + "】 管理群 【" + str(len(groups)) + "】 聊天在线 【" + str(len(user_in_chat)) + "】"
    return status_text


def heartbeat():
    '''
    定时报告进程状态
    '''
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


def condition_invite(user):
    '''
    条件邀请
    '''
    if user.sex == 2:
        female_groups = bot.groups().search(female_group)[0]
        try:
            female_groups.add_members(user, use_invitation=True)
            pass
        except:
            pass
    if (user.province in city_group.keys() or user.city in city_group.keys()):
        try:
            target_city_group = bot.groups().search(
                city_group[user.province])[0]
            pass
        except:
            target_city_group = bot.groups().search(city_group[user.city])[0]
            pass
        try:
            if user not in target_city_group:
                target_city_group.add_members(user, use_invitation=True)
        except:
            pass


def from_admin(msg):
    """
    判断 msg 中的发送用户是否为管理员
    :param msg:
    :return:
    """
    if not isinstance(msg, Message):
        raise TypeError('expected Message, got {}'.format(type(msg)))
    from_user = msg.member if isinstance(msg.chat, Group) else msg.sender
    return (from_user in admin_group) if admin_group else from_user == bot.self


def remote_kick(msg):
    '''
    远程踢人命令
    '''
    if msg.type is TEXT:
        match = rp_kick.search(msg.text)
        if match:
            name_to_kick = match.group(1)

            if not from_admin(msg):
                if not silence_mode:
                    return '感觉有点不对劲… @{}'.format(msg.member.name)
                else:
                    print('非管理员 {} 想踢人...'.format(msg.member.name))
                    return

            member_to_kick = ensure_one(
                list(
                    filter(lambda x: x.name == name_to_kick,
                           msg.sender.members)))
            if member_to_kick == bot.self:
                return '无法移出 @{}'.format(member_to_kick.name)
            if member_to_kick in admin_group.members:
                return '无法移出 @{}'.format(member_to_kick.name)

            logger_msg = get_time() + str(
                " 【" + member_to_kick.name + "】 被 【" + msg.member.name +
                "】 移出 【" + msg.sender.name + "】")
            try:
                member_to_kick.set_remark_name("[黑名单]-" + get_time())
            except:
                logger_msg += "\n" + str(
                    "为 【" + member_to_kick.name + "】 设置黑名单时出错")

            if member_to_kick in msg.chat:
                msg.chat.remove_members(member_to_kick)
                kick_info = '成功移出 @{}'.format(member_to_kick.name)
            else:
                kick_info = '@{} 已不在群中'.format(member_to_kick.name)

            for ready_to_kick_group in groups:
                if member_to_kick in ready_to_kick_group:
                    ready_to_kick_group.remove_members(member_to_kick)
                    ready_to_kick_group.send(
                        str("【" + member_to_kick.name + "】 因其在 【" +
                            msg.sender.name + "】 的行为被系统自动移出"))
                    logger_msg += "\n" + str(
                        "【" + member_to_kick.name + "】 被系统自动移出 " +
                        ready_to_kick_group.name)

            logger.error(logger_msg)
            return kick_info


def get_new_member_name(msg):
    '''
    邀请消息处理
    '''
    # itchat 1.2.32 版本未格式化群中的 Note 消息
    from itchat.utils import msg_formatter
    msg_formatter(msg.raw, 'Text')

    for rp in rp_new_member_name:
        match = rp.search(msg.text)
        if match:
            return match.group(1)


def invite(user, keyword):
    '''
    定义邀请用户的方法。
    按关键字搜索相应的群，如果存在相应的群，就向用户发起邀请。
    '''
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

def command_controller(msg):
    '''
    命令控制函数
    '''
    text = None
    if from_admin(msg):
        if msg.text == "#status":
            text = status()
        elif msg.text == "#restart":
            _restart()
            text = "准备重启"
        elif msg.text == "#refresh":
            fresh_groups()
            text = "群状态已更新\n" + status()
    return text

# 下方为消息处理

@bot.register()
def common_process(msg):
    '''
    所有消息注册函数
    控制台打印消息记录
    '''
    if msg_print:
        print(msg)
    random_sleep()

@bot.register(msg_types=FRIENDS)
def new_friends(msg):
    '''
    处理加好友请求信息。
    如果验证信息文本是字典的键值之一，则尝试拉群。
    '''
    common_process(msg)
    if msg.text.lower() in keyword_of_group.keys():
        user = msg.card.accept()
        random_sleep()
        user.send(invite_text)
        random_sleep()
        invite(user, msg.text.lower())
        random_sleep()
        condition_invite(user)

@bot.register(Friend, msg_types=TEXT)
def exist_friends(msg):
    common_process(msg)
    if msg.sender.name.find("黑名单") != -1:
        return "您已被拉黑！"
    elif msg.text.lower() in ["help", "帮助"]:
        msg.sender.send(help_text)
    elif msg.text.lower() in keyword_of_group.keys():
        invite(msg.sender, msg.text.lower())
    elif not silence_mode:
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
    random_sleep()
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
        random_sleep()
        return welcome_text.format(name)

@bot.register([bot.self, bot.file_helper, alert_receiver], except_self=False)
def alert_command(msg):
    controls = command_controller(msg)
    if not controls is None:
        return controls
    else:
        return exist_friends(msg)

embed()
