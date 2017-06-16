#!/usr/bin/env python3
# coding: utf-8

'''
为保证兼容，在下方admins中使用标准用法
在 admin_puids 中确保将机器人的puid 加入
机器人的puid 可以通过 bot.self.puid 获得
其他用户的PUID 可以通过 执行 export_puid.py 生成 data 文件，在data 文件中获取
'''
admin_puids = (
    '4c424ca7'
)

'''
定义需要管理的群
群的PUID 可以通过 执行 export_puid.py 生成 data 文件，在data 文件中获取
'''
group_puids = (
    '411b0ca5',
    '91c8eb0a'
)

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
"lfs":"LFS群"
}
机器人会以"LFS群"为群名搜索，搜索结果为同类群名的列表，
再从列表中随机选取一个发出加群邀请。
'''
keyword_of_group = {
    "测试":"机器人测试群",
    "bucm浙江":"北中医浙江老乡"
}

user_chat_on_text = "来聊天啦"
user_chat_on_reply = "来啦～想让我陪你聊什么呢？"
user_chat_off_text = "再见啦"
user_chat_off_reply = "拜～有事随时叫我哈～"

basic_help_text = """Yinr 微信助手使用说明
输入[help]或[帮助]可以查看本消息
"""

def menu_formater(key, title, is_group = False):
    text = "输入[{0}]可以{1}{2}"
    text = text.format(str(key), "申请加入" if is_group else "", title)
    return text

def fresh_help_text():
    help_text = basic_help_text
    help_text += menu_formater(user_chat_on_text, "在私聊中开始聊天") + '\n'
    help_text += menu_formater(user_chat_off_text, "在私聊中结束聊天") + '\n'
    for key in keyword_of_group:
        help_text += menu_formater(key, keyword_of_group[key], is_group = True)
        help_text += '\n'

fresh_help_text()

alter_user="Yinr"
alert_group="机器人测试群"

turing_key='e3bb6c563d0f48fc82b572bc842cc54d'
