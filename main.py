import json
import requests
import os
from dotenv import load_dotenv
import asana

load_dotenv()
NORTION_DATABASE_ID = os.environ.get('NORTION_DATABASE_ID')
NORTION_API_SECRET = os.environ.get('NORTION_API_SECRET')
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
ASANA_PERSONAL_ACCESS_TOKEN = os.environ.get('ASANA_PERSONAL_ACCESS_TOKEN')
ASANA_TEAM_GID = os.environ.get('ASANA_TEAM_GID')


def get_todo_from_nortion():
    url = f"https://api.notion.com/v1/databases/{NORTION_DATABASE_ID}/query"
    headers = {
        'Authorization': f'Bearer {NORTION_API_SECRET}',
        'Notion-Version': '2021-08-16',
        'Content-Type': 'application/json',
    }
    r = requests.post(url, headers=headers)
    return content_todo_from_nortion(r.json()['results'])


def content_todo_from_nortion(todo_results):
    todo_list = []
    for _todo in todo_results:
        todo = {
            'id': _todo['id'],
            'created_time': _todo['created_time'],
            'title': _todo['properties']['Name']['title'][0]['plain_text'],
            'status': _todo['properties']['Status']['select']['name']
            if _todo['properties']['Status']['select'] is not None else None,
        }
        todo_list.append(todo)

    return todo_list


def get_todo_from_asana():
    client = asana.Client.access_token(ASANA_PERSONAL_ACCESS_TOKEN)

    me = client.users.me()
    projects = client.projects.get_projects_for_team(team_gid=ASANA_TEAM_GID)

    sprint_project = {}
    for project in projects:
        sprint_project = project
        break

    tasks_mst = client.tasks.search_in_workspace(workspace=me['workspaces'][0]['gid'],
                                                 params={
                                                     'projects.any': sprint_project['gid'],
                                                     'assignee.any': me['gid']
                                                 })

    tasks = []
    for task_mst in tasks_mst:
        task = client.tasks.get_task(task_mst['gid'])
        tasks.append(task)

    return content_todo_from_asana(tasks)


def content_todo_from_asana(tasks):
    todo_list = []
    for task in tasks:
        todo = {
            'id': task['gid'],
            'created_time': task['created_at'],
            'title': task['name'],
            'status': task['memberships'][0]['section']['name']
        }
        todo_list.append(todo)

    return todo_list


def send_slack(todo_list, app='asana'):
    if app == 'nortion':
        status = ['Not started', 'In progress', 'Completed']
        complete = 'Completed'
    else:
        status = ['やること', '進行中', 'レビュー', '完了']
        complete = '完了'

    message = ''
    for _status in status:
        message = message + f"{_status}\n"
        for _todo in todo_list:
            if _todo['status'] == _status:
                if _todo['status'] == complete:
                    message = message + f" [x]{_todo['title']}\n"
                else:
                    message = message + f" []{_todo['title']}\n"

    message = '```' + message + '```'

    requests.post(SLACK_WEBHOOK_URL, data=json.dumps({
        'text': f"{message}",
        'username': u'koryBot',
        'icon_emoji': u':dog:',
        'link_names': 1,
    }))


if __name__ == '__main__':
    result = get_todo_from_asana()
    # result = get_todo_from_nortion()
    send_slack(result, 'asana')
