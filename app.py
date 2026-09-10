from flask import Flask, request, render_template, flash, session, redirect, url_for, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)


app.secret_key="123123098098"



def findChats(user):
    # user is user id
    connection=sqlite3.connect("database.db")
    cursor=connection.cursor()
    cursor.execute("SELECT chat_id FROM participants WHERE user_id=?",(user,))
    chats=cursor.fetchall()
    # returns list of chat ids
    return chats

@app.route('/chat/<user>/<int:chat>', methods=['GET'])
def chat(user,chat=1):
    # user is username chat is id
    if user in session:
        connection=sqlite3.connect("database.db")
        cursor=connection.cursor()
        #getting username and user object
        # cursor.execute("SELECT * FROM users WHERE username=?",(user,))
        # userob=cursor.fetchone()

        # getting all chat messages
        cursor.execute("SELECT * FROM chats WHERE id=?",(chat,))
        chats=cursor.fetchone()
        if chats==None:
            return "ERROR Chat not found"
        cursor.execute("SELECT messages.*, users.username FROM messages JOIN users ON messages.sender_id = users.id WHERE messages.chat_id=?",(chat,))
        messages=cursor.fetchall()

        chat_ids=findChats(session[user]["id"])
        chat_list=[]
        for id in chat_ids:
            cursor.execute("SELECT chat_name FROM chats WHERE id=?",(id,))
            chat=cursor.fetchall()
            chat_list.append(chat)

        last_id=messages[-1][0]

        connection.close()

        return render_template('chat.html', messages=messages, chatname=chats[1],chat_list=chat_list,user_id=session[user]["id"],chat_id=chats[0],username=user,last_message=last_id)
    return redirect(url_for('login'))

@app.route('/sendMessage',methods=['POST'])
def sendMessage():
    data=request.get_json()
    connection=sqlite3.connect("database.db")
    cursor=connection.cursor()
    timestamp=datetime.now()
    cursor.execute("INSERT INTO messages (chat_id,sender_id,content,timestamp) VALUES(?,?,?,?)",(data["chatid"],data["userid"],data["content"],timestamp))
    connection.commit()
    connection.close()
    return jsonify({
        "status": "success"
    }), 200
    
@app.route('/updateMessages',methods=['POST'])
def updateMessages():
    data=request.get_json()
    connection=sqlite3.connect("database.db")
    cursor=connection.cursor()

    cursor.execute("SELECT messages.*, users.username FROM messages JOIN users ON messages.sender_id = users.id WHERE messages.chat_id=? AND messages.id>?",(data["chatid"],data["lastmessage"]))
    new_messages=cursor.fetchall()
    connection.close()
    if new_messages==None:
        return jsonify({
            "updates": False
        }),200
    else:
        new_last_message=new_messages[-1][0]
        return jsonify({
            "updates": True,
            "new_messages":new_messages,
            "last_message":new_last_message
        }),200
    




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password=request.form['password']
        connection=sqlite3.connect("database.db")
        cursor=connection.cursor()
        try:
            # checking to see if if the username isn't already in the db
            cursor.execute("INSERT INTO users (username,password) VALUES(?,?)", (username,password))
            connection.commit()
            cursor.execute("SELECT * FROM users WHERE username=?",(username,))
            user=cursor.fetchone()
            session[username] = {
                "id": user[0],
                "all_chats": []
            }
            connection.close()
            return redirect(url_for('chat', user=username))

        except sqlite3.IntegrityError:
            flash("Username is already taken, please use a different one")
            
        connection.close()

    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username = request.form['username']
        password=request.form['password']
        connection=sqlite3.connect("database.db")
        cursor=connection.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?",(username,))
        user=cursor.fetchone()
        if user==None:
            flash("Username incorrect")
        elif user[2]==password:
            session[username] = {
                "id": user[0],
                "all_chats": findChats(user[0])
            }
            connection.close()
            return redirect(url_for('chat', user=username, chat=1))

        else:
            flash("Password incorrect")
        connection.close()
    
    return render_template('login.html')





   
if __name__ == '__main__':
    app.run(debug=True)