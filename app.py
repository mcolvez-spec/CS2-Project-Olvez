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
            flash("Email already exists!", "error")
        else:
            users[email] = {
                "username": username,
                "age": age,
                "address": address,
                "password": password_plain,
                "role": "user"
            }
            flash("Registration successful! Please login.", "success")
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
            flash("Invalid email or password", "error")

    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    global current_user
    if current_user:
        user = users[current_user]

        if request.method == "POST":
            req_text = request.form.get("request")
            if req_text:
                if current_user not in requests:
                    requests[current_user] = []
                requests[current_user].append(req_text)
                flash("Request submitted successfully!", "success")

        if user["role"] == "admin":
            return render_template("admindash.html", users=users, requests=requests)
        else:
            user_requests = requests.get(current_user, [])
            return render_template("dashboard.html", name=user["username"], requests=user_requests, email=current_user)

    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    global current_user
    current_user = None
    return redirect(url_for("login"))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    global current_user, users, requests
    if not current_user:
        return redirect(url_for('login'))

    user = users[current_user]

    if request.method == 'POST':
        current_pass = request.form.get('current_password')
        if not current_pass or current_pass != user['password']:
            flash('Current password is required and must be correct to update account.', 'error')
            return redirect(url_for('dashboard'))

        new_username = request.form.get('username')
        new_password = request.form.get('new_password')
        new_email = request.form.get('email')

        changed = False
        if new_username and new_username != user.get('username'):
            user['username'] = new_username
            changed = True

        if new_password:
            user['password'] = new_password
            changed = True

        if new_email and new_email != current_user:
            if new_email in users:
                flash('That email is already in use.', 'error')
                return redirect(url_for('dashboard'))
            users[new_email] = users.pop(current_user)
            if current_user in requests:
                requests[new_email] = requests.pop(current_user)
            current_user = new_email
            flash('Email changed successfully.', 'success')

        if changed:
            flash('Profile updated successfully.', 'success')
        else:
            flash('No changes applied.', 'error')

        return redirect(url_for('dashboard'))

    return redirect(url_for('dashboard'))

@app.route('/admin/edit/<target_email>', methods=['GET', 'POST'])
def admin_edit(target_email):
    global current_user, users, requests
    if not current_user:
        return redirect(url_for('login'))
    admin = users.get(current_user)
    if not admin or admin.get('role') != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('dashboard'))

    target = users.get(target_email)
    if not target:
        flash('User not found.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'GET':
        return render_template('admindash.html', users=users, requests=requests, edit_target=target, edit_target_email=target_email)

    admin_pass = request.form.get('admin_password')
    if admin_pass:
        if admin_pass != admin['password']:
            flash('Admin password is required and must be correct to perform this action.', 'error')
            return redirect(url_for('dashboard'))

    new_username = request.form.get('username')
    new_password = request.form.get('password')
    new_email = request.form.get('email')
    new_role = request.form.get('role')
    new_age = request.form.get('age')
    new_address = request.form.get('address')

    if new_username:
        target['username'] = new_username
    if new_password:
        target['password'] = new_password
    if new_role:
        target['role'] = new_role
    if new_age:
        try:
            target['age'] = int(new_age)
        except Exception:
            target['age'] = new_age
    if new_address:
        target['address'] = new_address

    if new_email and new_email != target_email:
        if new_email in users:
            flash('That email is already in use.', 'error')
            return redirect(url_for('dashboard'))
        users[new_email] = users.pop(target_email)
        if target_email in requests:
            requests[new_email] = requests.pop(target_email)
        if target_email == current_user:
            current_user = new_email
        flash('Admin email change applied.', 'success')

    flash('User updated successfully.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/admin/delete/<target_email>', methods=['GET', 'POST'])
def admin_delete(target_email):
    global current_user, users, requests
    if not current_user:
        return redirect(url_for('login'))
    admin = users.get(current_user)
    if not admin or admin.get('role') != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('dashboard'))

    target = users.get(target_email)
    if not target:
        flash('User not found.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'GET':
        return render_template('admindash.html', users=users, requests=requests, delete_target=target, delete_target_email=target_email)

    admin_pass = request.form.get('admin_password')
    if not admin_pass or admin_pass != admin['password']:
        flash('Admin password is required and must be correct to delete an account.', 'error')
        return redirect(url_for('dashboard'))

    if target_email == admin_email:
        flash('The main admin account cannot be deleted.', 'error')
        return redirect(url_for('dashboard'))

    if target_email in users:
        users.pop(target_email)
    if target_email in requests:
        requests.pop(target_email)

    if target_email == current_user:
        current_user = None
        flash('Account deleted. You have been logged out.', 'success')
        return redirect(url_for('login'))

    flash('Account deleted.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/request/delete/<owner_email>/<int:index>', methods=['POST'])
def delete_request(owner_email, index):
    global current_user, users, requests
    if not current_user:
        return redirect(url_for('login'))

    user = users.get(current_user)
    is_admin = user and user.get('role') == 'admin'

    # Users can only delete their own; admins can delete anyone's
    if not is_admin and owner_email != current_user:
        flash('You can only delete your own requests.', 'error')
        return redirect(url_for('dashboard'))

    owner_requests = requests.get(owner_email, [])
    if index < 0 or index >= len(owner_requests):
        flash('Request not found.', 'error')
        return redirect(url_for('dashboard'))

    owner_requests.pop(index)
    requests[owner_email] = owner_requests
    flash('Request deleted.', 'success')
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(debug=True)