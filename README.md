# task-notification-from-asana-or-nortion

## セットアップ
```
pip install -r requirements.txt
cp .env.sample .env
```

### Asana Personal access token
https://app.asana.com/0/developer-console

### Nortion integration
https://www.notion.so/my-integrations

### Slack Incoming Webhook
https://slack.com/services/new/incoming-webhook

### AsanaかNortionどちらから取るか
```
if __name__ == '__main__':
    result = get_todo_from_asana()
    # result = get_todo_from_nortion()
    send_slack(result, 'asana')
```

## 実行
```
python main.py
```