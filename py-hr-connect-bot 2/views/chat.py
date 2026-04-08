from pkg_imp import app, render_template, session, sessionRequired

@app.route('/chat')
@sessionRequired
def chat(user):
    return render_template('chat/chat-main.html')

