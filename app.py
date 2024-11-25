from flask import Flask,render_template,redirect,request,url_for,session
from flask_mysqldb import MySQL
app = Flask(__name__)


app.secret_key = 'haujui'

#CREATING A CONNECTION TO THE DATABASE
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'webdeveloper'
app.config['MYSQL_PASSWORD'] = 'florence77'
app.config['MYSQL_DB'] = 'soichat'

mysql = MySQL(app)

@app.route('/')
def homepage():
    print("Homepage accesed")
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user_reg")
    user_reg = cur.fetchall()
    cur.close()
    return render_template('index.html', users=user_reg)

@app.route('/chat')
def chat():
    if 'user_id' in session:
        #connecting with registered users for new chats purposes
        cur = mysql.connection.cursor()
        table_name = session['user_Name']
        selectingChats = f"SELECT * FROM `{table_name}.FRIENDS`"
        cur.execute(selectingChats)

        friends = cur.fetchall()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user_reg")
        user_reg = cur.fetchall()
        cur.close()
        return render_template('chat.html', users=user_reg, friends=friends)
    
    else :
        return redirect('/')

@app.route('/chatss', methods=['GET','POST'])
def chatss():
    if 'user_id' in session:
        if request.method == 'POST':
            friendName = request.form['friend']
            session['friendName'] = friendName
            cur = mysql.connection.cursor()
            selectingChats = f"SELECT * FROM `{session['user_Name']}.CHAT_{friendName}`"
            cur.execute(selectingChats)
            messages = cur.fetchall()
            cur.close()
            cur = mysql.connection.cursor()
            table_name = session['user_Name']
            selectingChats = f"SELECT * FROM `{table_name}.FRIENDS`"
            cur.execute(selectingChats)

            friends = cur.fetchall()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM user_reg")
            user_reg = cur.fetchall()
            cur.close()
            return render_template('chats.html',messages=messages,users=user_reg, friends=friends)

        else :
                friendName = session.get('friendName')
                cur = mysql.connection.cursor()
                selectingChats = f"SELECT * FROM `{session['user_Name']}.CHAT_{friendName}`"
                cur.execute(selectingChats)
                messages = cur.fetchall()
                cur.close()
                cur = mysql.connection.cursor()
                table_name = session['user_Name']
                selectingChats = f"SELECT * FROM `{table_name}.FRIENDS`"
                cur.execute(selectingChats)

                friends = cur.fetchall()
                cur.close()
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM user_reg")
                user_reg = cur.fetchall()
                cur.close()
                return render_template('chats.html', messages=messages,users=user_reg, friends=friends)
    else :
                return redirect('/')

#route for signing up
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':    #requesting the values from the signup form
        fullName = request.form['fullName']
        userName = request.form['userName']
        email = request.form['email']
        password = request.form['password']
        Aob = request.form['AOB']
        db_name = userName
        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO user_reg (fullName,userName,email,password,AOB) values(%s,%s,%s,%s,%s)""",(fullName,userName,email,password,Aob)) #inserting the values to the mysql table
        tableCreationQuery = f"CREATE TABLE `{db_name}.FRIENDS` (id INT AUTO_INCREMENT PRIMARY KEY,friendName VARCHAR (255))"
        cur.execute(tableCreationQuery)
        mysql.connection.commit()
        cur.close()
        return redirect('/')

#route for loging in
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        userName = request.form['userName']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user_reg WHERE userName = %s AND password = %s",(userName,password))
        user = cur.fetchone()
        cur.close()
        #validating if the user exists
        if user:
            session['user_id'] = user[0]
            session['user_Name'] = user[2]
            return redirect(url_for('chat'))
        else :
            return redirect('/')

#route for loging out
@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        session.pop('user_id',None)
        session.pop('user_Name',None)
        return redirect('/')

#ROUTE FOR ADDING NEW FRIEND
@app.route('/newfriend', methods=['POST'])
def newfriend():
    if request.method == 'POST':
        if 'user_id' in session:
            friendName = request.form['friendName']
            userName = friendName
            ownerName = session['user_Name']
            cur = mysql.connection.cursor()
            insertingFriend = f"INSERT INTO `{session['user_Name']}.FRIENDS` (friendName) values(%s)"
            acceptingFriend = f"INSERT INTO `{friendName}.FRIENDS` (friendName) values(%s)"
            creatingMessageTable1 = f"CREATE TABLE `{session['user_Name']}.CHAT_{userName}` (id INT AUTO_INCREMENT PRIMARY KEY,msgsent VARCHAR (1000),msgrecieved VARCHAR (1000))"
            creatingMessageTable2 = f"CREATE TABLE `{userName}.CHAT_{session['user_Name']}` (id INT AUTO_INCREMENT PRIMARY KEY,msgsent VARCHAR (1000),msgrecieved VARCHAR (1000))"
            cur.execute(creatingMessageTable1)
            cur.execute(creatingMessageTable2)
            cur.execute(acceptingFriend,(ownerName,))
            cur.execute(insertingFriend,(friendName,))
            mysql.connection.commit()
            cur.close()
            

            return redirect(url_for('chat'))
    else :
        return redirect('/')

#ROUTE FOR MESSAGING
@app.route('/message', methods=['POST'])
def message():
    if 'user_id' in session:
        if request.method == 'POST':
            message = request.form['message']
            cur = mysql.connection.cursor()
            insertingMessagesent = f"INSERT INTO `{session['user_Name']}.CHAT_{session['friendName']}` (msgsent) values(%s)"
            insertingMessagerecieved = f"INSERT INTO `{session['friendName']}.CHAT_{session['user_Name']}` (msgrecieved) values(%s)"
            cur.execute(insertingMessagesent,(message,))
            cur.execute(insertingMessagerecieved,(message,))
            mysql.connection.commit()
            cur.close()

            return redirect('/chatss')
    else:
        return redirect('/')

@app.route('/chatgpt')
def chatgpt():
    return render_template('w3.html')


if __name__  == '__main__' :
    
    app.run(host='0.0.0.0', port=5001, debug=True)