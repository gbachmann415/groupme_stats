import requests
import json
import pandas as pd
from config.credentials import ACCESS_TOKEN, groupID

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

URL = "https://api.groupme.com/v3/"

endpoints = ["groups", "chats", "direct_messages", "bots", "users", "blocks"]

PAGE = 1

def mapGroupsWithIDs():
    PARAMS = {"token": ACCESS_TOKEN,
              "page": PAGE,
              "per_page": 100}

    requestURL = URL + "groups"

    response = requests.get(url=requestURL, params=PARAMS)

    data = json.dumps(response.json(), indent=3)

    data = json.loads(data)

    df = pd.DataFrame.from_dict(data['response'])

    df = df[['name', 'group_id']]

    groupIDMapping = dict(zip(df.name, df.group_id))

    return groupIDMapping

def getTopTenLikes(period, groupID):
    PARAMS = {"period": period,
              "token": ACCESS_TOKEN}

    requestURL = URL + f"groups/{groupID}/likes"

    response = requests.get(url=requestURL, params=PARAMS)

    data = json.dumps(response.json(), indent=3)

    data = json.loads(data)

    df = pd.DataFrame.from_dict(data['response']['messages'])

    df = df[['name', 'text', 'attachments', 'favorited_by']]
    df['likes'] = None

    count = 0
    for i in df['favorited_by']:
        total = len(i)
        df['likes'][count] = total
        count += 1

    return df[['name', 'likes']]

def getMessages(groupID):
    PARAMS = {"token": ACCESS_TOKEN,
              "limit": 100}

    requestURL = URL + f"groups/{groupID}/messages"

    response = requests.get(url=requestURL, params=PARAMS)

    data = json.dumps(response.json(), indent=3)
    # print(data)

    data = json.loads(data)

    df = pd.DataFrame.from_dict(data['response']['messages'])

    df = df[['name', 'user_id', 'id']]
    lastID = df['id'].iloc[-1]
    


def main():
    # getTopTenLikes("month", groupID)
    # mapGroupsWithIDs()
    getMessages(groupID)


main()
