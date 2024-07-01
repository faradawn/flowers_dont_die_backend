# Backend Setup
CC-Ubuntu 20.04 (6.6G). Default Python version: 3.8.10.

## SSH to server
```
ssh -i my_private_key cc@129.114.24.200
```

## Setup FastAPI
```
# update the environment
sudo apt update
sudo apt upgrade -y
sudo apt install python3-pip python3-venv -y

# install fastapi and firebase
python3 -m venv env
source env/bin/activate
pip install fastapi uvicorn
pip install --upgrade firebase-admin

# (optional) for baidu qianfan (requires creating venv python3.9)
pip install --upgrade appbuilder-sdk

# put firebase key inside /backend folder and name it as
faradawn_private_key.json

# launch the app on port 8001
tmux
uvicorn app.main:app --host 0.0.0.0 --port 8001

# on another terminal
curl http://127.0.0.1:8001

# on local computer
curl http://129.114.24.200:8001
```



### Test API
```
# Post 01
curl -X POST "http://129.114.24.200:8001/courses" \
     -H "Content-Type: application/json" \
     -d '{"uid": "100"}'
```

### Trouble shoot
- Installation error: grpcio-status 1.64.1 has requirement protobuf<6.0dev,>=5.26.1, but you'll have protobuf 4.25.3 which is incompatible.
Solution:
```
pip install grpcio-status==1.62.2
```

- "422 Unprocessable Entity". Solved by defining the input request's base model.
```
# before
async def garden_page_load(uid: int, course_id: int):

# after
async def garden_page_load(request: PageLoadRequest):

class PageLoadRequest(BaseModel):
    uid: int
    course_id: int
```

- If firewall issue and can't access the API
```
# First check
sudo ufw status

# Second check
sudo systemctl status firewalld
sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --add-port=8001/tcp
sudo firewall-cmd --reload
```

- How to invoke a script
```
# add the project root
python -m app.scripts.firebase_delete_all_users
```

- How to use Claude API
```
pip install anthropic
pip install python-dotenv

# Then put API Key in app/.env

cd app/scripts
python3 calude_ai.py
```