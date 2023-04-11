from flask import Flask, request

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('example.db')
    c = conn.cursor()

    # Check if the username and password match
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    row = c.fetchone()
    conn.close()

    if row is None:
        # If no match is found, return an error message
        return "Invalid username or password"
    else:
        # If a match is found, return a success message
        return "Login successful"

if __name__ == '__main__':
    app.run(debug=True)