# coding: utf-8

from inspect import formatannotationrelativeto
import os
import datetime
import uuid
from slack_bolt import App
from slack_sdk.errors import SlackApiError
import requests
from airtable import Airtable
from datetime import date
from dotenv import load_dotenv
load_dotenv()

# ボットトークンと署名シークレットを使ってアプリを初期化
app = App(
    token=os.environ.get("SLACK_USER_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

client = app.client


# 'hello'を含むメッセージをリッスンします
# 指定可能なリスナーのメソッドの引数の一覧は以下を参考に

@app.message("hello")
def message_hello(message, say, ack):
    ack()
    # イベントがトリガーされたチャンネルへsay()でメッセージを送信します
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"報告書を作成しますか？ <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "作成します"},
                    "action_id": "button_click"
                }
            }
        ],
        text=f"報告書を作成しますか？ <@{message['user']}>!"
    )

# 特定のコマンドでチャンネルを開きます


@app.action("button_click")
def action_button_click(body, ack, say, logger):
    print("button click module started")
    # アクションを確認したことを即時で応答します
    ack()
    print(body)
    # チャンネルにメッセージを投稿します
    say(f"<@{body['user']['id']}> clicked the button")

    # チャンネルを作成します
    dtnow = datetime.datetime.now()
    # UUIDを使用して、他と被らないようにする
    namestr = '事案-{}-{}-{}-{}-{}-{}-{}-{}'.format(dtnow.year, dtnow.month, dtnow.day,
                                                  dtnow.hour, dtnow.minute, dtnow.second, dtnow.microsecond, uuid.uuid4())
    try:
        result = client.conversations_create(

            name=namestr
        )
        logger.info(result)

    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))
        print("Error creating conversation: {}".format(e))
    except Exception as e:
        print(e)

    # チャンネル作成に成功していたら、チャンネルに作成者を招待します
    if(result['ok']):
        userid = body['user']['id']
        channel_id = result['channel']['id']

        client.conversations_join(
            channel=channel_id
        )
        client.conversations_invite(
            channel=channel_id,
            users=userid
        )


@app.message("history")
def history(ack, body, say, logger):

    # airtable upload用
    his = []
    ack()
    channelHis = body['event']['channel']
    #channelHis = 'C02DM3V39UJ'

    his = client.conversations_history(channel=channelHis)

    for i in his.data['messages']:
        mes_recur(i)


def mes_recur(message):
    # messageを受け取る
    # textの時はtextだけ、fileがあるときはfileとサムネイルのみの投稿にする
    # アーカイブの場合は再帰する

    if('files' in message.keys()):
        # airtableの添付ファイルは、ダウンロードurlを要求する

        for fileitm in message['files']:
            if(fileitm['is_public'] is False):
                r = client.files_sharedPublicURL(file=fileitm['id'])
            # ファイル毎にアップロードする
            if(fileitm['filetype'] != 'gif'):
                r = airtable_upload(attach=fileitm['permalink_public'])

    if('attachments' in message.keys()):
        for attc in message['attachments']:
            r = mes_recur(attc)

    if('attachments' not in message.keys() and 'files' not in message.keys()):
        # attachmentsとfilesの両方が無い時のみ、textをairtableにアップロードする
        r = airtable_upload(note=message['text'])


# チャンネルをアーカイブします
@app.message("delete")
def tehepero(ack, body, logger):
    # アクションを確認した事を応答
    ack()
    print(body)
    channel_del = body['event']['channel']
    app.client.conversations_archive(
        channel=channel_del
    )


def airtable_upload(kaishi='', note='', attach='', channel='', key='', table_name='記録'):
    # 報告情報をairtableにアップロードする
    # 開始時間
    # ノート
    # 添付
    # チャンネル

    # Airtable(baseID,table_name,api_key)
    airtable = Airtable(os.environ.get('AIRTBL_REPORTBASEID'),
                        table_name, os.environ.get('AIRTBL_API_KEY'))
    record = {'ノート': note,
              '添付': attach,
              'チャンネル': channel,
              'キー': key}
    tmp = {}
    for k, v in record.items():
        if(v != ''):
            tmp[k] = v

    record = tmp

    r = airtable.insert(record, typecast=True)
    return r

# replace withuyour personal access token.
personal_access_token = '1/1201052327944929:f7e1d98e50cea2663998df60f3ba73ca'



def asana_upload():
    
# Construct an Asana client
client = asana.Client.access_token(personal_access_token)
#client = asana.Client.oauth(
#        client_id='clientid',
#        client_secret='clientsecret',
import asana
#from .gen.attachments import _Attachments
clientid = os.environ.get('ASANA_CLIENT_ID')
clientsecret = os.environ.get('ASANA_CLIENT_SECRET')
# replace withuyour personal access token.
personal_access_token = os.environ.get('ASANA_PERSONAL_ACCESS')
# Construct an Asana client
client = asana.Client.access_token(personal_access_token)
#client = asana.Client.oauth(
#        client_id='clientid',
#        client_secret='clientsecret',
#        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
#        )
(url, state) = client.session.authorization_url()
#if request.params['state'] == state:
#  token = client.session.fetch_token(code=request.params['code'])
  # ...
#else:
  # error! possible CSRF attack
# Set things up to send the name of this script to us to show that you succeeded! This is optional.
#client.options['client_name'] = "ReportManager"
# Get your user info
#me = client.users.me()
# Print out your information
#print("Hello world! " + "My name is " + me['name'] + "!")
task_gid = '1201052281703499'
attachment_gid = '1201052281703503'
#result = client.attachments.delete_attachment(task_gid,opt_pretty=True)
result = client.attachments.create_on_task(task_id=task_gid,file_content=open('/tmp/videos/anomaly.gif', 'rb'),file_name='    testgif.gif',file_content_type="image/gif")

# アプリを起動します
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
