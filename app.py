from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "secretkey123"

users = {}
requests = {}
current_user = None  

admin_email = "princegwaps@gmail.com"
users[admin_email] = {
    "username": "migs",
    "name": "Prince Gwapo",
    "password": "gwapokayosiprince",  
    "role": "admin",
    "age": 14,
    "address": "pisay"
}

@app.route("/")
def home():
    global current_user
    if current_user:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        age = request.form["age"]
        address = request.form["address"]
        email = request.form["email"]
        password_plain = request.form["password"]

        if email in users:
            flash("Email already exists!")
        else:
            users[email] = {
                "username": username,
                "age": age,
                "address": address,
                "password": password_plain,
                "role": "user"
            }
            flash("Registration successful! Please login.")
            return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    global current_user
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = users.get(email)
        if user and user["password"] == password:
            current_user = email   
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password")

    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    global current_user
    if current_user:
        user = users[current_user]

        if request.method == "POST":
            req_text = request.form["request"]
            if current_user not in requests:
                requests[current_user] = []
            requests[current_user].append(req_text)
            flash("Request submitted successfully!")

        if user["role"] == "admin":
            return render_template("admindash.html", users=users, requests=requests)
        else:
            user_requests = requests.get(current_user, [])
            return render_template("dashboard.html", name=user["username"], requests=user_requests)

    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    global current_user
    current_user = None
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)