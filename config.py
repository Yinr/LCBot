#!/usr/bin/env python3
# coding: utf-8
'''
定义管理员群的名称

在该群内的人都将被设为管理员，
管理员在被管理的群中享有高级管理权限，可进行如踢人等的操作
注：群名为部分匹配，请尽量输入全名以保证搜索到的群的唯一性
'''
admin_group_name = '机器人管理员群'
'''
定义被管理群的群名前缀
所有以此为前缀的群都将设为被管理的群
注：前缀大小写敏感

如：设定为'Linux中国◆'，则将自动搜索到
「Linux中国◆微信机器人群」「Linux中国◆LFS群」等以其为开头的群，
并将其设为被管理的群
'''
group_prefix = '机器人'
'''
定义非特定前缀的群

注：必须输入完整名称
'''
additional_groups = ('另一个机器人群', )

# 新人入群的欢迎语
welcome_text = '''🎉 欢迎 @{} 的加入！
😃 有问题请私聊我。
'''

invite_text = """欢迎您，我是 Yinr 微信助手，
如果您有好的机器人使用想法，
欢迎与我分享"""
'''
设置群组关键词和对应群名
* 关键词必须为小写，查询时会做相应的小写处理

关于随机加群功能：
针对同类的群有多个的场景，例如群名 LFS群1、LFS群2、LFS群3...
设置关键词字典如下：
keyword_of_group = {
    "lfs":"LFS群",
}
机器人会以"LFS群"为群名搜索，搜索结果为同类群名的列表，
再从列表中随机选取一个发出加群邀请。
'''
keyword_of_group = {
    "测试": "机器人测试群",
    "bucm浙江": "北中医浙江老乡",
}
'''
地区群
'''
city_group = {
    "北京": "机器人北京群",
}

keyword_of_group.update(city_group)

female_group = ""

user_chat_on_text = "来聊天啦"
user_chat_on_reply = "来啦～想让我陪你聊什么呢？"
user_chat_off_text = "再见啦"
user_chat_off_reply = "拜～有事随时叫我哈～"

help_command = ['help', '帮助']

turing_key = 'e3bb6c563d0f48fc82b572bc842cc54d'

alert_level = 30  # DEBUG: 10, INFO: 20, WARNING: 30, ERROR: 40, FATAL: 50
alert_user = "Yinr"
alert_group = "机器人监控群"

basic_help_text = """Yinr 微信助手使用说明"""

# 以下为功能配置选项
'''
全局静默开关
'''
silence_mode = False

# 以下是函数定义


def menu_formater(keys, title, is_group=False):
    keys_text = keys if isinstance(keys, str) else ']或['.join(list(keys))
    text = ">>输入[{0}]\n{1}{2}"
    text = text.format(keys_text, "申请加入" if is_group else "", title)
    return text


def fresh_help_text():
    help_text = basic_help_text

    help_text += "\n「命令帮助」\n"
    help_text += menu_formater(help_command, '查看本帮助消息') + '\n'
    if turing_key:
        help_text += menu_formater(user_chat_on_text, "在私聊中开始机器人聊天") + '\n'
        help_text += menu_formater(user_chat_off_text, "在私聊中结束机器人聊天") + '\n'

    help_text += "\n「加群指南」\n"
    for key in keyword_of_group:
        help_text += menu_formater(key, keyword_of_group[key], is_group=True)
        help_text += '\n'

    help_text += "注：以上命令都不包括'['和']'"
    return help_text


help_text = fresh_help_text()
