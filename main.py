import requests
import json
import pandas as pd
from config.credentials import ACCESS_TOKEN, groupID

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

URL = "https://api.groupme.com/v3/"

endpoints = ["groups", "chats", "direct_messages", "bots", "users", "blocks"]

PAGE = 0


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


def main():
    getTopTenLikes("month", groupID)


main()
