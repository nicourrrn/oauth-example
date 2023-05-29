from fastapi import FastAPI, Request, Cookie, WebSocket
from fastapi.responses import RedirectResponse
import requests
import asyncio

from typing import Annotated

app = FastAPI()

state = 'sadfasdjfkasdf'
# https://github.com/settings/developers -> OAuth apps
client_id = ""
client_secret = ""

users = {}

@app.get('/')
async def main(req: Request):
    user_id = req.query_params.get('user_id')
    print(req.query_params)
    if user_id is None:
        return {"status": "Bad request"}
    
    global users 
    if user_id in users.keys() and users[user_id] != "":
        return users[user_id] 
    resp = RedirectResponse("https://github.com/login/oauth/authorize?\
&client_id={client_id}\
&redirect_uri=http://localhost:8000/callback\
&scope=repo+read:org\
&state={state}".format(client_id=client_id, state=state))
    resp.set_cookie(key="session", value=user_id)
    return resp

@app.get('/callback')
async def callback(req: Request, session: Annotated[str | None, Cookie()]):
    code = req.query_params['code']
    print(req.query_params)

    resp = requests.get(
            "https://github.com/login/oauth/access_token?\
&grant_type=authorization_code\
&client_id={client_id}\
&client_secret={client_secret}\
&code={code}".format(client_id=client_id, client_secret=client_secret, code=code)).text
    user_data = dict([s.split('=') for s in resp.split('&')]) 
    global users
    users[session] = user_data['access_token']
    return user_data 



@app.get('/user_name')
async def get_name(session: Annotated[str | None, Cookie()]):
    global users
    resp = requests.get("https://api.github.com/user",
            headers={
                    'Accept': 'application/vnd.github+json',
                    'Authorization': f'Bearer {users[session]}',
                    'X-GitHub-Api-Version': '2022-11-28'
                })
    return resp.json() 

@app.websocket('/get_token')
async def get_token(websoc: WebSocket):
    await websoc.accept()
    session = await websoc.receive_text()
    global users
    while True:
        if users.get(session) is not None:
            await websoc.send_text(users[session])
        await asyncio.sleep(1)

