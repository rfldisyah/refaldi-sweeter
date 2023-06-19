from flask import (
    Flask,
    render_template, 
    jsonify, 
    request, 
    session, 
    redirect, 
    url_for,
)

from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__)
MONGODB_CONNECTION_STRING = 'mongodb+srv://test:refaldi@cluster0.tjgiegp.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.dbsparta_project4

SECRET_KEY = 'SPARTA'

@app.route('/', methods=['GET'])
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(
            token_receive, 
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.user.find_one({'id': payload['id']})
        return render_template('index.html', nickname=user_info['nick'])
    except jwt.ExpiredSignatureError:
        return redirect(url_for(
            'login',
            msg="Your login token has expired"
        ))
    except jwt.exceptions.DecodeError:
            return redirect(url_for(
            'login',
            msg="There was in issue logging your in"
        ))
    
@app.route('/login', methods=['GET'])
def login():
     msg = request.args.get('msg')
     return render_template('login.html', msg=msg)


@app.route('/register', methods=['GET'])
def register():
     return render_template('register.html')


@app.route('/api/register', methods=['POST'])
def api_register():
     id_receive = request.form.get('id_give')
     pw_receive = request.form.get('pw_give')
     nickname_receive = request.form.get('nickname_give')
     pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

     db.user.insert_one({
          'id': id_receive,
          'pw': pw_hash,
          'nick': nickname_receive,
     })

     return jsonify({ 'result': 'success' })




@app.route('/api/login', methods=['POST'])
def api_login():
     id_receive = request.form.get('id_give')
     pw_receive = request.form.get('pw_give')
     pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
     result = db.user.find_one({
          'id': id_receive,
          'pw': pw_hash,
     })
     if result: 
          payload = {
               'id': id_receive,
               'exp': datetime.utcnow() + timedelta(seconds=5)
          }
          token = jwt.encode(
               payload,
               SECRET_KEY,
               algorithms=['HS256']
          )
          return jsonify ({
               'result': 'succes',
               'token': token
          })
     else:
          return jsonify({
               'result': 'fail',
               'msg': 'Either your id or your password is incorect',
          })
     


@app.route('/api/nick', methods=['GET'])
def api_valid():
     token_receive = request.cookies.get('mytoken')
     try:
          payload = jwt.decode(
               token_receive,
               SECRET_KEY,
               algorithms=['HS256']
          )
          print(payload)
          user_info = db.user.find_one({'id': payload.get('id')}, {'_id': 0})
          return jsonify({
               'result': 'success',
               'nickname': user_info.get('nick')
          })

     except jwt.ExpiredSignatureError:
        msg= "Your login token has expired"
        return jsonify({'result': 'fail', 'msg':msg})
     except jwt.exceptions.DecodeError:
        msg= "There was in issue logging your in"
        return jsonify({'result': 'fail', 'msg':msg})

if __name__ == '__main__':
     app.run('0.0.0.0', port=5000, debug=True)
