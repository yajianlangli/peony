from flask import \
    render_template,\
    redirect,\
    url_for,\
    session
import sqlite3
from notebookOnWeb.forms import *
from notebookOnWeb import app
import hashlib
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 80))
ip = s.getsockname()[0]
s.close()

conn = sqlite3.connect("data.db",check_same_thread=False)
cursor = conn.cursor()

try:
    cursor.execute(
        """
        CREATE TABLE users(
            name        CHAR(10) PRIMARY KEY    NOT NULL,
            pswdhash    CHAR(40)                NOT NULL吧ggggggt
        );
        """
    )
    conn.commit()
except Exception as e:print(e)

try:
    cursor.execute(
        """
        CREATE TABLE notes(
            topic    CHAR(20)    NOT NULL,
            name     CHAR(10)    NOT NULL,
            note     CHAR(20000) NOT NULL,
            notehash CHAR(40)    NOT NULL,
            public   INTEGER     NOT NULL,
            stars    INT         NOT NULL
        );
        """
    )
    conn.commit()
except Exception as e:print(e)

@app.route('/notes')
def notes():
    global ip
    cursor.execute("SELECT topic FROM notes WHERE name=? OR public=1",(session.get('usr'),))
    topics = list(set(cursor.fetchall()))
    return render_template(
        'notes.html',
        usr=session.get('usr'),
        topics=topics,
        ip=ip
    )

@app.route('/users')
def users():
    global ip
    cursor.execute("SELECT topic,name FROM notes WHERE name=? OR public=1",(session.get('usr'),))
    topics = list(set(cursor.fetchall()))
    cursor.execute("SELECT name FROM users")
    users = list(set(cursor.fetchall()))
    return render_template(
        'users.html',
        usr=session.get('usr'),
        topics=topics,
        users=users,
        ip=ip
    )

@app.route('/')
def toHome(): # go back home
    return render_template('index.html',
                          title='欢迎来到',
                          usr=session.get('usr'),
                          ip=ip)

@app.route('/login',methods=['GET','POST'])
def login():
    global ip
    loginform = loginForm()
    if loginform.validate_on_submit():
        cursor.execute("SELECT pswdhash FROM users WHERE name = ?",(loginform.username.data,))
        res = cursor.fetchone() or [None]
        if res[0] == hashlib.md5(bytes(loginform.userpass.data,encoding='utf-8')).hexdigest():
            session['usr'] = loginform.username.data
            return redirect("/")
        else:
            return render_template('login.html',
                                  title='用户名或密码错误，请重新登陆',
                                  form=loginform,
                                  usr=session.get('usr'),
                                  ip=ip)
    return render_template('login.html',
                          title='登录',
                          form=loginform,
                          usr=session.get('usr'),
                          ip=ip)

@app.route('/edit',methods=['GET','POST'])
def edit():
    global ip
    editform = editForm()
    if not session.get('usr'):
        return redirect(url_for("login"))
    if editform.validate_on_submit():
        cursor.execute("INSERT INTO notes VALUES (?,?,?,?,?)",(
            editform.topic.data,
            session['usr'],
            editform.note.data,
            hashlib.md5(bytes(editform.note.data,encoding='utf-8')).hexdigest(),
            editform.public.data,
            0,))
        conn.commit()
        return redirect(url_for("notes"))
    return render_template('editnotes.html',
                          title='写下你的想法',
                          form=editform,
                          usr=session.get('usr'),
                          ip=ip)

@app.route('/del/<hash_>',methods=['GET','POST'])
def delete(hash_):
    cursor.execute("DELETE FROM notes WHERE notehash = ?",(hash_,))
    conn.commit()
    return redirect("/")

@app.route('/logon',methods=['GET','POST'])
def logon():
    global ip
    logonform = logonForm()
    if logonform.validate_on_submit():
        cursor.execute("SELECT pswdhash FROM users WHERE name = ?",
                          (logonform.username.data,))
        if cursor.fetchone():
            return render_template('logon.html',
                                  title='用户名已存在',
                                  form=logonform,
                                  usr=session.get('usr'),
                                  ip=ip)
        cursor.execute("INSERT INTO users VALUES (?,?)",(
            logonform.username.data,
            hashlib.md5(bytes(logonform.userpass.data,encoding='utf-8')).hexdigest()))
        conn.commit()
        session['usr'] = logonform.username.data
        return redirect("/")
    return render_template('logon.html',
                          title='注册',
                          form=logonform,
                          usr=session.get('usr'),
                          ip=ip)

@app.route('/logout',methods=['GET','POST'])
def logout():
    session.pop('usr',None)
    return redirect("/")

@app.route('/shownotes/<topic>')
def shownotes(topic):
    global ip
    cursor.execute("SELECT name,note FROM notes WHERE topic=? AND (name=? OR public=1)",
                  (topic,session.get('usr')))
    notes = cursor.fetchall()
    return render_template('shownotes.html',
                          title='主题为{}的知识本'.format(topic),
                          notes=notes,
                          usr=session.get('usr'),
                          hashlib=hashlib,
                          bytes=bytes,
                          ip=ip)
