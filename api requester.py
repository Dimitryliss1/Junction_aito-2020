import requests
from requests.structures import CaseInsensitiveDict
import json
import random

url = 'https://junction2020.aito.app/api/v1'
api_key = "0pJDlYxnu29G4fB52vqFe6OW6DfgfOt7a96WkrnM"    # public read API-key
headers = CaseInsensitiveDict()
teams_ids = set()
headers["x-api-key"] = api_key
headers["Content-Type"] = "application/json"


def return_schema():    # for getting a schema of a project
    return requests.get(url+'/schema', headers=headers).json()


def get_item(usr_location: str, props: dict, limit: int, offset: int):    # Props are required to be as in an example in Aito.ai API
    data = dict()
    data["from"] = usr_location
    data["where"] = props
    data["limit"] = limit
    data["offset"] = offset
    data = json.dumps(data)

    return requests.post(url+'/_search', data=data, headers=headers).json()


def create_an_entry(props: dict, table: str):   # props should correspond to their schemas in a database
    return requests.post(url+'/data/{}'.format(table), data=props, headers=headers).json()


def create_an_entry_batch(props: list, table: str):     # props is a list of props-dicts(refer to create_an_entry)
    result = list()
    for i in props:
        result.append(requests.post(url+'/data/{}'.format(table), data=i, headers=headers).json())
    return result

def delete(where_to_delete: str, what_to_delete: dict):     # to remove an entry. What_to_delete is a dict just like in get_item
    data = dict()
    data["from"] = where_to_delete
    data["where"] = what_to_delete
    data = json.dumps(data)
    return requests.post(url+'/data/_delete', headers=headers, data=data).json()


def recommend(team: list):    # team is a list of dicts of users, formed by client
    data = dict()
    data["from"] = "ratings"
    if len(team) == 1:
        data["where"] = {"userID": team[0]}
    else:
        data["where"] = {"$and": list({"userID": i} for i in team)}
    data["recommend"] = "placeID"
    data["goal"] = {"rating": 2}
    data = json.dumps(data)
    return requests.post(url+ '/_recommend', headers=headers, data=data).json()


def create_team(team: list):  # list of userid's. Assume that we have a field "teams" in user's field
    unique_id = ''
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_+'
    for i in range(10):
        unique_id += alphabet[random.randint(0, 64)]
    while unique_id in teams_ids:
        unique_id = ''
        for i in range(10):
            unique_id += alphabet[random.randint(0, 64)]
    teams_ids.add(unique_id)
    for i in team:
        data = dict()
        data["from"] = "users"
        data["where"] = {"userID": i}
        result = requests.post(url+'/_search', headers=headers, data=data)
        if result.status_code >= 400:
            raise ConnectionError
        else:
            requests.post(url+'/data/_delete', headers=headers, data=data)
            result = result.json()
            result["teams"] += unique_id+';'    # teams field -- list of team-ids separated with ;
            result = json.dumps(result)
            create_an_entry(result, 'users')


def delete_team(team_id: str):
    data = dict()
    data["from"] = "users"
    data["where"] = {"teams": team_id}
    result = get_item('users', data["where"], 100000, 0)
    for i in result:
        teams = result[i]["teams"].split(";")
        del teams[teams.index(team_id)]
        new = ''
        for j in teams:
            new += j
            new += ';'
        new = new[:-1]
        result[i]["teams"] = new
        delete('users', {"userID": result[i]["userID"]})
        create_an_entry(result[i], 'users')



# print(recommend([{
#         "activity": "student",
#         "ambience": "family",
#         "birth_year": 1989,
#         "budget": "medium",
#         "color": "black",
#         "cuisine": "American",
#         "dress_preference": "informal",
#         "drink_level": "abstemious",
#         "height": 1.77,
#         "hijos": "independent",
#         "interest": "variety",
#         "latitude": 22.139997,
#         "longitude": -100.978803,
#         "marital_status": "single",
#         "payment": "cash",
#         "personality": "thrifty-protector",
#         "religion": "none",
#         "smoker": "false",
#         "transport": "on foot",
#         "userID": "U1001",
#         "weight": 69
#     }, {
#         "activity": "student",
#         "ambience": "family",
#         "birth_year": 1990,
#         "budget": "low",
#         "color": "red",
#         "cuisine": "Mexican",
#         "dress_preference": "informal",
#         "drink_level": "abstemious",
#         "height": 1.87,
#         "hijos": "independent",
#         "interest": "technology",
#         "latitude": 22.150087,
#         "longitude": -100.983325,
#         "marital_status": "single",
#         "payment": "cash",
#         "personality": "hunter-ostentatious",
#         "religion": "Catholic",
#         "smoker": "false",
#         "transport": "public",
#         "userID": "U1002",
#         "weight": 40
#     }]))
# print(create_team(['abacabba']))