from flask import Flask, jsonify, render_template ,request ,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configuring the SQLite database, stored in a file called 'sas.db' in your project folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # to disable a warning

db = SQLAlchemy(app)

class PayAndSave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_paid_for = db.Column(db.String(100), nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    amount_to_save = db.Column(db.Float, nullable=False)
    receiver_phone_number = db.Column(db.String(15), nullable=False)

class Withdraw(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount_to_withdraw = db.Column(db.Float, nullable=False)
    withdraw_to_number = db.Column(db.String(15), nullable=False)

class SavingsGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal_name = db.Column(db.String(100), nullable=False)  # Goal name, required
    target_amount = db.Column(db.Float, nullable=False)    # Target amount to save
    target_date = db.Column(db.Date, nullable=False)  
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(10), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)    # Date by which goal should be achieved
    def __repr__(self):
        return f'<User {self.username} - {self.phone}>'
    def __repr__(self):
        return f'<SavingsGoal {self.goal_name} - {self.target_amount} by {self.target_date}>'

@app.route('/')
def home():
    return render_template('dashboard.html')  # or any file like home.html

@app.route('/auth')
def auth():
    return render_template('login.html')

@app.route('/register',methods=['POST'])
def register():
     data = request.get_json()
     phone = data['phone']
     password = data['password']
     username = data['username']

     if User.query.filter_by(phone=phone).first():
        return jsonify({'status': 'fail', 'message': 'Phone already exists'}), 409
     
     # hashed_password = generate_password_hash(password)

     user = User(phone=phone, username=username)
     user.set_password(password)
     db.session.add(user)
     db.session.commit()

     return jsonify({'status': 'success', 'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    
    data = request.get_json()
    phone = data['phone']
    password = data['password']

    user = User.query.filter_by(phone=phone).first()


    if user and user.check_password(password):
        return jsonify({'status': 'success', 'username': user.username})
    else:
        return jsonify({'status': 'fail', 'message': 'Invalid credentials'}), 
      

@app.route('/get_started')
def get_started():
    return render_template('get_started.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/add_transaction', methods=['POST'])
def handle_add_transaction():
    print("RAW form data:", request.form)
    product = request.form.get('product')
    amount = request.form.get('amount')
    save = request.form.get('save')
    number = request.form.get('number')

    #am now creating a  new pay and svae object 
    new_transaction = PayAndSave(
        product_paid_for=product,
        amount_paid=float(amount),
        amount_to_save=float(save),
        receiver_phone_number=number
    )

    # adding to database and commiting them 
    db.session.add(new_transaction)
    db.session.commit()

    
    message= f"Transaction recorded . Saved : UGX {save} on {product}. Paid UGX {amount} to {number}"
    return render_template('success.html',message=message)
    print(f"Saved to DataBase : {new_transaction}")
    
    return redirect('/')

@app.route('/withdraw',methods=['POST'])
def handle_withdraw():
    Withdraw_amount = request.form.get('Withdraw')
    phone_number = request.form.get('tel')

    print(f"Withdraw: {Withdraw_amount} to number: {phone_number}")
    # let me now save to database
    new_withdraw = Withdraw(
        amount_to_withdraw=float(Withdraw_amount),
        withdraw_to_number=phone_number
    )
    db.session.add(new_withdraw)
    db.session.commit()

    message =f"Withdraw request of UGX {Withdraw_amount} to {phone_number} has been recorded."
    return render_template('success.html', message=message)



from datetime import datetime
from flask import Flask, render_template, request, redirect, flash
@app.route('/set_goal', methods=['POST'])
def handle_set_goal():
    # if method=='POST':
    goal_name = request.form.get('goal-name')
    goal_amount = request.form.get('goal-amount')
    goal_date = request.form.get('goal-date')

    # Basic validation
    if not goal_name or not goal_amount or not goal_date:
        flash('All fields are required.', 'danger')
        return redirect('/')

    # Convert date string to Python date object
    try:
        target_date = datetime.strptime(goal_date, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format.', 'danger')
        return redirect('/')

    try:
        amount = float(goal_amount)
    except ValueError:
        flash('Amount must be a number.', 'danger')
        return redirect('/dashboard')

    # Save to database
    new_goal = SavingsGoal(
        goal_name=goal_name,
        goal_amount=amount,
        goal_date=target_date
    )
    print(new_goal)
    db.session.add(new_goal)
    db.session.commit()
    print(new_goal)

    message = f"You have set a goal: {goal_name} to save UGX {amount} by {target_date}"
    print(f"✅ Saved to DB: {new_goal}")
    return render_template('success.html', message=message)



















# @app.route('/set_goal', methods=['POST'])
# def handle_set_goal():
#     goal_name = request.form.get('goal-name')
#     goal_amount = request.form.get('goal-amount') 
#     goal_date = request.form.get('goal-date')


#    # target_date = datetime.strptime(goal_date, '%Y-%m-%d').date()
#     # print("⚠️ Invalid date format")
#        # return redirect('/')


#     print(f"Goal : {goal_name}, Amount : {goal_amount},Date: {goal_date}")
    
#     # Converting  string date to Python date object
#     #try:
#       # except ValueError:
# ## return redirect('/')
    
#     #am saving  to db

#     new_goal = SavingsGoal(
#         goal_name=goal_name,
#         target_amount=float(goal_amount),
#         target_date=goal_date
#     )
#     db.session.add(new_goal)
#     db.session.commit()
    
#     message =f"You have set a goal: {goal_name} to save UGX {goal_amount} by {goal_date}"
#     return render_template('success.html', message=message)
#     print(f"Saved to DataBase : {new_goal}")
#     return redirect('/')

# @app.route('/set_goal', methods=['POST'])
# def handle_set_goal():
#     goal_name = request.form.get('goal-name')
#     goal_amount = request.form.get('goal-amount')
#     goal_date = request.form.get('goal-date')

#     # Basic validation
#     if not goal_name or not goal_amount or not goal_date:
#         flash('All fields are required.', 'danger')
#         return redirect('/')

#     # Convert date string to Python date object
#     try:
#         target_date = datetime.strptime(goal_date, '%Y-%m-%d').date()
#     except ValueError:
#         flash('Invalid date format.', 'danger')
#         return redirect('/')

#     try:
#         amount = float(goal_amount)
#     except ValueError:
#         flash('Amount must be a number.', 'danger')
#         return redirect('/dashboard')

#     # Save to database
#     new_goal = SavingsGoal(
#         goal_name=goal_name,
#         target_amount=amount,
#         target_date=target_date
#     )
#     db.session.add(new_goal)
#     db.session.commit()

#     message = f"You have set a goal: {goal_name} to save UGX {amount} by {target_date}"
#     print(f"✅ Saved to DB: {new_goal}")
#     return render_template('success.html', message=message)

    

    
if __name__ == '__main__':
    with app.app_context():
        print("Creating database tables...")
        print("Current working directory:", os.getcwd())
        db.create_all()  # This will create the SQLite db file and tables if not exist
    # app.run(debug=True)


