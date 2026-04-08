import flask
from flask_cors import CORS
import datetime, uuid, decimal, os, json, base64, requests
from flask import render_template, send_from_directory, request, session, abort, redirect
from llama_index import SimpleDirectoryReader, VectorStoreIndex, PromptHelper, LLMPredictor,\
ServiceContext
from llama_index.llms import OpenAI, anthropic
from modules.c2Crypt import crypt
from functools import wraps
import config
from json import JSONEncoder
import orjson
from flask.json.provider import JSONProvider
import openai
from modules.dbConnector import mongoConnector
from bson.objectid import ObjectId


app = flask.Flask(__name__)
CORS(app)
app.config.from_object(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = "vishnu-csq-chat"


class MyJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.__str__()
        if isinstance(o, datetime.date):
            return o.__str__()
        if isinstance(o, decimal.Decimal):
            return float(o.__str__())
            
app.json_encoder = MyJSONEncoder # type: ignore

class OrJSONProvider(JSONProvider):
    def dumps(self, obj, *, option=None, **kwargs):
        if option is None:
            option = orjson.OPT_APPEND_NEWLINE | orjson.OPT_NAIVE_UTC
        
        return orjson.dumps(obj, option=option).decode()

    def loads(self, s, **kwargs):
        return orjson.loads(s)

# assign to an app instance
app.json = OrJSONProvider(app)

class InterceptRequestMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        environ['HTTP_X_REQUEST_ID'] = str(uuid.uuid4())
        environ['HTTP_X_REQUEST_TIME'] = str(datetime.datetime.timestamp(datetime.datetime.utcnow()))
        return self.wsgi_app(environ, start_response)

app.wsgi_app = InterceptRequestMiddleware(app.wsgi_app)

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY_HERE")
openai.api_key = os.environ["OPENAI_API_KEY"]

# OpenAIindex = GPTSimpleVectorIndex.load_from_disk('/index.json')
print("loading Docs")
documents = SimpleDirectoryReader('docs').load_data()
print("loading Indexes")
OpenAIindex = VectorStoreIndex.from_documents(documents)
print("Indexes loaded")
service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo-0613"))
AI_query_engine = OpenAIindex.as_query_engine()
AI_chat_engine = OpenAIindex.as_chat_engine(verbose=True,chat_mode='react') # type: ignore

allow_dummy_session = True

# if os.path.exists('index.json'):
#     with app.open_resource('index.json', 'r') as f:
#         s = f.read()

#     OpenAIindex = VectorStoreIndex.load_from_string(s)

Crypto = crypt()

def setSession(token):
    # try:
    if True:
        _token = json.loads(base64.b64decode(token))
        if session.get('auth_token') == token:
            return 

        _url = f"{config.CSQ_SSO_BASE_URL}/csquare/login/session/{_token['session_id']}?flag=1"
        _r = requests.get(_url)
        if _r.status_code != 200:
            if session.get('logged_in') and session['code'] == _token['user_code']:
                return 

            if session:
                session.clear()

            abort(401)

        if session:
            session.clear()

        session['logged_in'] = True
        session['mobile'] = _token['mobile']
        session['code'] = _token['user_code']
        session['name'] = _token['user_name']
        session['session_id'] = _token['session_id']
        session['auth_token'] = token

        user = str(_token['mobile'])
        session['user'] = sessionEncode(user)
        # menus = [
        #     # {'title': "HR Help", 'href': "/chat", 'ico': "message-circle"},
        #     # {'title': "HR Help - Admin", 'href': "/chat-config", 'ico': "sliders"},
        #     # {'title': "License Management", 'href': "https://1c2.in/csq-lic/web/licenseManagement", 'ico': "monitor"}
        # ]
        # session['menu'] = menus
        profile = {
            'name': _token['user_name'],
            'note': "C-Square",
            'csqLicAdmin': True
        }

        session['profile'] = profile

    # except Exception as e:
    #     print(e)
    #     pass

def get_home_url():
    _url = request.host_url + config.APP_HOME_URL
    _url = _url.replace('http://127.0.0.1:5003', config.APP_BASE_URL)
    _args = ""
    for _arg in request.args:
        if _arg == "auth_token":
            continue

        _args += ('&' if _args != '' else '') + _arg + "=" + request.args.get(_arg) # type: ignore

    if _args != '':
        _url += "?" + _args

    return _url

@app.errorhandler(401)
def login_req(e):
    _url = request.base_url
    _url = _url.replace('http://127.0.0.1:5003', config.APP_BASE_URL)
    _args = ""
    for _arg in request.args:
        if _arg == "auth_token":
            continue

        _args += ('&' if _args != '' else '') + _arg + "=" + request.args.get(_arg) # type: ignore

    if _args != '':
        _url += "?" + _args

    return redirect(f"{config.CSQ_SSO_BASE_URL}/csquare/login?redirect_url={_url}")

@app.before_request
def handle_before_request():
    if request.args.get('auth_token'):
        setSession(request.args.get('auth_token'))

def sessionEncode(v):
    key = session.get('key')
    if not key:
        key = str(uuid.uuid4())
        key = Crypto.encrypt(key, app.config['SECRET_KEY'])
        session['key'] = key

    key = Crypto.decrypt(key, app.config['SECRET_KEY'])

    return Crypto.encrypt(v, key)

def sessionDecode(v):
    key = session.get('key')
    key = Crypto.decrypt(key, app.config['SECRET_KEY'])

    v = Crypto.decrypt(v, key)
    return v

def create_dummy_session():
    session.clear()
    session['user'] = sessionEncode("dummyuser")
    session['profile'] = {
        "name": "Dummy User",
        "note": "C-Square Info-Solutions Limited"
    }


def sessionRequired(f):
    @wraps(f)
    def validate(*args, **kwargs):
        user = session.get('user')
        print("user", user)
        if not user:
            if allow_dummy_session:
                create_dummy_session()
                user = session.get('user')
            else:
                abort(401)
  
        try:
            # decoding the payload to fetch the stored details
            user = sessionDecode(user)
            if not user:
                abort(401)

        except:
            abort(401)

        # returns the current logged in users contex to the routes
        return  f(user, *args, **kwargs)
  
    return validate

MONGO_CHAT = mongoConnector(config.MONGO_HOST, config.MONGO_DB, config.MONGO_CONN_POOL_SIZE)
