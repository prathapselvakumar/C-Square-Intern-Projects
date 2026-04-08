
from pkg_imp import app, request, session, PromptHelper, LLMPredictor, SimpleDirectoryReader, \
    OpenAI, sessionRequired, AI_query_engine, OpenAIindex, AI_chat_engine, MONGO_CHAT, datetime, \
    ObjectId

class User:
    def __init__(self, mobile) -> None:
        self.mobile = mobile
        self.session_id = None
        self.session_status = 0
        self.session_history = []
        pass

    def get_session(self, **kargs):
        session_id = kargs.get('session_id')
        if session_id:
            if self.load_session(session_id):
                self.session_id = session_id
                return
        
        session_list = MONGO_CHAT.DB["session_mst"].find_one({"mobile": self.mobile, "status": 1})
        if not session_list:
            r = self.create_session()
            return r
        
        self.session_id = str(session_list['_id'])
        self.session_status = session_list['status']
        self.get_history()
        return self.session_id
    
    def reset_session(self):
        self.session_id = None
        self.session_status = 0
        self.session_history = []

    def load_session(self, session_id):
        self.reset_session()
        session = MONGO_CHAT.DB["session_mst"].find_one({"_id": ObjectId(session_id)})
        if not session:
            return False
        
        self.session_id = session_id
        self.session_status = session['status']
        self.get_history()

    def create_session(self):
        t = {
            'mobile': self.mobile,
            'start_time': datetime.datetime.utcnow(),
            'end_time': None,
            'status': 1,
            'last_update': datetime.datetime.utcnow()
        }

        r = MONGO_CHAT.DB["session_mst"].insert_one(t)
        self.reset_session()
        self.session_id = str(r.inserted_id)
        self.session_status = 1
        self.session_history = []

        return self.session_id
    
    def get_history(self):
        if not self.session_id:
            return False
        
        self.session_history = list(MONGO_CHAT.DB["session_det"].find({"session_id": ObjectId(self.session_id)}))
        return self.session_history
    
    def add_history(self, q, a):
        t = {'session_id': ObjectId(self.session_id), 'q': q, 'a': a}
        self.session_history.append(t)
        
        MONGO_CHAT.DB["session_det"].insert_one(t)
        MONGO_CHAT.DB["session_mst"].update_one({"_id": ObjectId(self.session_id)}, 
                {"$set": {"last_update": datetime.datetime.utcnow()}})

    def close_session(self, session_id):
        session = MONGO_CHAT.DB["session_mst"].find_one({"_id": ObjectId(session_id)})
        if not session:
            self.reset_session()
            return
        
        MONGO_CHAT.DB["session_mst"].update_one({"_id": ObjectId(session_id)}, 
                {"$set": {"last_update": datetime.datetime.utcnow(),
                        "end_time": datetime.datetime.utcnow(), "status": 0}})


class Message:
    def __init__(self, userFrom, userTo, **kargs) -> None:
        self.user = User(userFrom)
        self.user.get_session(session_id=session.get('chat_session_id'))
        session['chat_session_id'] = self.user.session_id
        self.text = kargs.get('text')
        self.history = self.user.session_history
        if not self.history:
            self.history = []

        self.history = [(x['q'], x['a']) for x in self.history]
        
        pass

    def get_reply(self):
        print(self.text)
        response = AI_query_engine.query(self.text)
        print(response)
        return response.response
    
    def send_chat(self):
        chat_engine = OpenAIindex.as_chat_engine(verbose=True,
                #chat_history=self.history
                )
        # response = AI_chat_engine.chat(self.text)
        response = chat_engine.chat(self.text)
        self.add_history(self.text, str(response).strip())
        
        return str(response).strip()
    
    def add_history(self, q, a):
        self.history.append((q, a))
        self.user.add_history(q, a)
        # h = session['history']
        # h.append({"q": q, "a": a})
        # session['history'] = h


@app.route('/chat/send-message', methods=["POST"])
@sessionRequired
def chat_send_message(user):
    fromUser = user
    data = request.json
    toUser = data['to']
    text = data['text']

    message = Message(fromUser, toUser, text=text)

    return {'status': True, 'statusMessage': "Message sent", 'response': message.get_reply()}
    #return {'status': True, 'statusMessage': "Message sent", 'response': message.send_chat()}

@app.route('/chat/clear-history', methods=["GET"])
@sessionRequired
def chat_clear_history(user):
    user = User(user)
    user.close_session(session_id=session.get('chat_session_id'))
    session["chat_session_id"] = user.create_session()
    return "History cleared"

# @app.route('/chat/generate-json', methods=["GET"])
# @sessionRequired
# def chat_generate_json(user):
#     directory_path = "docs"
#     max_input_size = 4096
#     num_outputs = 512
#     max_chunk_overlap = 20
#     chunk_size_limit = 600

#     prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)
#     llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.3, model_name="gpt-3.5-turbo", max_tokens=num_outputs))

#     documents = SimpleDirectoryReader(directory_path).load_data()
#     index = GPTSimpleVectorIndex.from_documents(documents)
#     index.save_to_disk('index.json')

#     with open('index.json', 'r') as f:
#         s = f.read()

#     s = s.replace("\n", "")
#     # s = s.replace("\u25aa", "")
#     with open('index.json', 'w') as f:
#         f.write(s)

#     return ""
