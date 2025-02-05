from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import pymysql
import uuid

# Install pymysql for MySQL
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session tracking

# Configure Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://jai:admin123@localhost/common_contributions_tracker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)

# Define Message Model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    admin_reply = db.Column(db.String(500), nullable=True)

# Ensure database is created
with app.app_context():
    db.create_all()

@app.before_request
def assign_user_id():
    """ Assigns a unique user ID for new users. """
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())  # Unique user ID for anonymous users

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_messages')
def get_messages():
    """ Fetches messages for users or admin. """
    if session.get("is_admin"):  # If admin, show all messages
        messages = Message.query.all()
    else:  # Normal users see only their messages
        messages = Message.query.filter_by(user_id=session['user_id']).all()

    return jsonify([{"id": msg.id, "message": msg.message, "admin_reply": msg.admin_reply} for msg in messages])

@app.route('/send_message', methods=['POST'])
def send_message():
    """ Saves messages to the database """
    user_id = session['user_id']
    message_text = request.form.get('message')

    if message_text:
        new_message = Message(user_id=user_id, message=message_text)
        db.session.add(new_message)
        db.session.commit()

    return '', 204

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    """ Simple admin login (replace with proper authentication) """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Dummy admin credentials (Replace with database authentication)
        if username == "admin" and password == "admin123":
            session["is_admin"] = True  # Set admin flag
            return redirect(url_for('admin_dashboard'))

    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    """ Admin panel for viewing all messages """
    if not session.get("is_admin"):
        return redirect(url_for('admin_login'))  # Redirect unauthorized users

    return render_template('admin.html')

@app.route('/admin/reply', methods=['POST'])
def admin_reply():
    """ Allows admin to reply to messages """
    if not session.get("is_admin"):
        return '', 403  # Forbidden for non-admins

    message_id = request.form.get('message_id')
    admin_reply_text = request.form.get('admin_reply')

    message = Message.query.get(message_id)

    if message:
        message.admin_reply = admin_reply_text
        db.session.commit()

    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    """ Logout user/admin """
    session.clear()  # Clear session data
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
