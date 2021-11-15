import requests
import json
import pandas as pd
from config.credentials import ACCESS_TOKEN, groupID

pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.max_rows', 5000)

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
    return df[['name', 'likes', 'text', 'attachments']]

def getMessages(groupID, lastID=None):
    PARAMS = {"token": ACCESS_TOKEN,
              "limit": 100,
              "before_id": lastID}

    requestURL = URL + f"groups/{groupID}/messages"

    response = requests.get(url=requestURL, params=PARAMS)

    data = json.dumps(response.json(), indent=3)

    data = json.loads(data)

    df = pd.DataFrame.from_dict(data['response']['messages'])

    df = df[['name', 'user_id', 'id']]

    lastID = df['id'].iloc[-1]

    while response.status_code == 200:
        PARAMS = {"token": ACCESS_TOKEN,
                  "limit": 100,
                  "before_id": lastID}
        response = requests.get(url=requestURL, params=PARAMS)
        if response.status_code != 200: break

        tempData = json.dumps(response.json(), indent=3)

        tempData = json.loads(tempData)

        tempDF = pd.DataFrame.from_dict(tempData['response']['messages'])

        tempDF = tempDF[['name', 'user_id', 'id']]
        lastID = tempDF['id'].iloc[-1]

        df = df.append(tempDF, ignore_index=True)

    # uniqueUserIDs = list(df['user_id'].unique())

    """
    Make note that if going by name instead of user_id, it won't include all messages for a person if their name has changed
    """
    totalCount = df['user_id'].value_counts()
    # totalCount = df['name'].value_counts()

    finalDF = pd.DataFrame(data=totalCount).reset_index()
    finalDF = finalDF.rename(columns={"index": "user_id", "user_id": "count"})
    finalDF['name'] = None

    user_id_mapping = dict(zip(df.user_id, df.name))

    for i in range(len(finalDF) - 1):
        if finalDF['name'][i] == None:
            name = user_id_mapping[finalDF['user_id'][i]]
            # print(f"user_id: {finalDF['user_id'][i]} -- name: {name}")
            finalDF['name'][i] = name

    print(finalDF)



def main():
    top_ten = getTopTenLikes("month", groupID)
    print(top_ten)
    # mapGroupsWithIDs()
    # getMessages(groupID)


main()
