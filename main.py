from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import requests

app = FastAPI()

state = 'sadfasdjfkasdf'
user_data = {}
# https://github.com/settings/developers -> OAuth apps
client_id = ""
client_secret = ""

@app.get('/')
async def main():
    global user_data
    if user_data.get('access_token') is not None:
        return user_data
    return RedirectResponse("https://github.com/login/oauth/authorize?\
&client_id={client_id}\
&redirect_uri=http://localhost:8000/callback\
&scope=repo+read:org\
&state={state}".format(client_id=client_id, state=state))

@app.get('/callback')
async def callback(req: Request):
    code = req.query_params['code']
    print(req.query_params)

    resp = requests.get(
            "https://github.com/login/oauth/access_token?\
&grant_type=authorization_code\
&client_id={client_id}\
&client_secret={client_secret}\
&code={code}".format(client_id=client_id, client_secret=client_secret, code=code)).text
    global user_data
    user_data = dict([s.split('=') for s in resp.split('&')]) 
    return user_data 



@app.get('/user_name')
async def get_name():
    global user_data
    resp = requests.get("https://api.github.com/user",
            headers={
                    'Accept': 'application/vnd.github+json',
                    'Authorization': f'Bearer {user_data["access_token"]}',
                    'X-GitHub-Api-Version': '2022-11-28'
                })
    return resp.json() 
