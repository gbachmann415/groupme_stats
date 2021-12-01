"""
Author: Gunnar Bachmann

Program that uses the GroupMe API to extract and manipulate data in order to produce various statistics.
"""
import requests
import json
import pandas as pd
from pandasgui import show

from config.credentials import ACCESS_TOKEN, groupID, GMAIL_SENDER, GMAIL_TO

pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.max_rows', 5000)

URL = "https://api.groupme.com/v3/"

endpoints = ["groups", "chats", "direct_messages", "bots", "users", "blocks"]

PAGE = 1

"""
Return a dataframe of all groups with their title and group ID
"""
def map_groups_with_ids():
    PARAMS = {"token": ACCESS_TOKEN,
              "page": PAGE,
              "per_page": 100}

    requestURL = URL + "groups"

    response = requests.get(url=requestURL, params=PARAMS)

    data = json.dumps(response.json(), indent=3)

    data = json.loads(data)

    df = pd.DataFrame.from_dict(data['response'])

    df = df[['name', 'group_id']]

    group_id_mapping = dict(zip(df.name, df.group_id))

    return group_id_mapping


"""
Given a period (day, week, month) and a group ID, return a dataframe of the top ten most liked messages.
Dataframe includes: date, users name, likes, text, attachments.
"""
def get_top_ten_likes(period, groupID):
    PARAMS = {"period": period,
              "token": ACCESS_TOKEN}

    requestURL = URL + f"groups/{groupID}/likes"

    response = requests.get(url=requestURL, params=PARAMS)

    data = json.dumps(response.json(), indent=3)

    data = json.loads(data)

    df = pd.DataFrame.from_dict(data['response']['messages'])

    df = df[['name', 'text', 'attachments', 'favorited_by', 'created_at']]
    df['likes'] = None

    count = 0
    for i in df['favorited_by']:
        total = len(i)
        df.loc[count, 'likes'] = total
        count += 1

    df['created_at'] = pd.to_datetime(df['created_at'], unit='s')

    return df[['created_at', 'name', 'likes', 'text', 'attachments']]


"""
Return a dataframe of the total message count within a group for each user.
"""
def get_messages(groupID, lastID=None):
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
            # finalDF['name'][i] = name
            finalDF.loc[i, 'name'] = name

    return finalDF


"""
Organize and clean the attachments column in a Dataframe.
"""
def organize_attachments(df):
    count = 0
    for cell in df['attachments']:
        cell_attachments = []
        for j in cell:
            if 'url' in j:
                cell_attachments.append(j['url'])
        df.at[count, 'attachments'] = cell_attachments
        count += 1

    return df

# TODO create a function that cleans a dataframe (like capitalizing column titles) for email

"""
Main method
"""
def main():
    # Call function to get top ten most liked messages
    top_ten = get_top_ten_likes("month", groupID)
    # Organize the attachments column in the top_ten dataframe
    top_ten = organize_attachments(top_ten)

    print(top_ten)

    # # Get mapping for each group and their IDs
    # group_id_mapping = map_groups_with_ids()

    # # Get total message count for each user within a group
    # messages_df = get_messages(groupID)

    # # Ask the user if they would like to launch the pandas GUI
    # show_gui = input("Do you want to open the messages data in a GUI? [yes] ")
    # if show_gui == 'yes':
    #     show(top_ten, messages_df)

    return


# main()
