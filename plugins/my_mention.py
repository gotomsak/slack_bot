from slackbot.bot import respond_to
from slackbot.bot import listen_to
from slackbot.bot import default_reply


@respond_to('メンション')
def mention_func(message):
    message.reply('私にメンションといってどうするのだ')

@listen_to('リッスン')
def listen_func(message):
    message.send('誰かリッスンと投稿したようだ')
    message.reply('君だね？')

@respond_to('かっこいい')
def cool_func(message):
    message.reply('ありがとう。スタンプをやろう！')
    message.react('+1')

@respond_to('ありがとう')
def Appreciation(message):
    message.reply('礼などいらぬ')
    message.react('blush')
"""
def_word='デフォルトの返事です'
@default_reply(r'^set\s+')
def default_func(message):
    message.reply(def_word)


@respond_to(r'^set\s+\S.*')
def set_default_func(message):
    text=message.body['text']
    temp,word=text.split(None,1)
    global def_word
    def_word=word
    msg='デフォルトの返事を以下のように変更しました。\n```'+word+'```'
    message.reply(msg)
"""

@respond_to(r'^ping\s+\d+\.\d+\.\d+\s*$')
def ping_func(message):
    message.reply('それはpingのコマンドですね。実行できませんが')

"""
@respond_to(r'.+')
def all_respond_func(message):
    text=message.body['text']
    msg='あなたの送ったメッセージは\n```'+text+'```'
    message.reply(msg)
"""

