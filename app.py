from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

app.config['SECRET_KEY'] = 'your_secret_key'

# Database config (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///requests.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Mail config (use your real SMTP details)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jovelynestadola@gmail.com'         # your email here
app.config['MAIL_PASSWORD'] = 'zxkpdqmjcjnjafqs'     # your email app password here
mail = Mail(app)

# Hardcoded manager emails
MANAGER_EMAIL = "jovelynestadola@gmail.com"
GENERAL_MANAGER_EMAIL = "jovelynestadola@gmail.com"

class PowerInterruptionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100))
    employee_email = db.Column(db.String(100))   # Add employee email to notify
    reason = db.Column(db.Text)
    outage_date = db.Column(db.String(20))
    outage_time = db.Column(db.Integer)
    affected_area = db.Column(db.String(100))
    manager_approved = db.Column(db.Boolean, default=None)  # None = pending
    general_manager_approved = db.Column(db.Boolean, default=None)

def create_tables():
    with app.app_context():
        db.create_all()



@app.route('/', methods=['GET', 'POST'])
def submit_request():
    if request.method == 'POST':
        new_req = PowerInterruptionRequest(
            employee_name=request.form['employee_name'],
            employee_email=request.form['employee_email'],  # get employee email here
            reason=request.form['reason'],
            outage_date=request.form['outage_date'],
            outage_time=int(request.form['outage_time']),
            affected_area=request.form['affected_area']
        )
        db.session.add(new_req)
        db.session.commit()

        # Email to manager
        msg = Message(
            subject='Power Interruption Request Approval Needed',
            sender=app.config['MAIL_USERNAME'],
            recipients=[MANAGER_EMAIL],
            body=f"""
Employee {new_req.employee_name} submitted a power interruption request.

Reason: {new_req.reason}
Date: {new_req.outage_date}
Outage Time: {new_req.outage_time} hours
Affected Area: {new_req.affected_area}

Please approve or reject here:
http://localhost:5000/approve_manager/{new_req.id}
"""
        )
        mail.send(msg)

        flash('Request submitted! Manager has been notified.', 'success')
        return redirect(url_for('submit_request'))
    return render_template('form.html')


# @app.route('/approve_manager/<int:req_id>', methods=['GET', 'POST'])
# def approve_manager(req_id):
#     req = PowerInterruptionRequest.query.get_or_404(req_id)

#     if request.method == 'POST':
#         action = request.form['action']
#         if action == 'approve':
#             req.manager_approved = True

#             # Notify employee about manager approval
#             msg_emp = Message(
#                 subject='Your Power Interruption Request - Manager Approved',
#                 sender=app.config['MAIL_USERNAME'],
#                 recipients=[req.employee_email],
#                 body=f"""
# Hello {req.employee_name},

# Your power interruption request has been approved by the Manager.

# Reason: {req.reason}
# Date: {req.outage_date}
# Outage Time: {req.outage_time} hours
# Affected Area: {req.affected_area}

# The request is now pending General Manager approval.

# Thank you.
# """
#             )
#             mail.send(msg_emp)

#             # Email to General Manager
#             msg_gm = Message(
#                 subject='Power Interruption Request - General Manager Approval Needed',
#                 sender=app.config['MAIL_USERNAME'],
#                 recipients=[GENERAL_MANAGER_EMAIL],
#                 body=f"""
# Manager approved the power interruption request by {req.employee_name}.

# Reason: {req.reason}
# Date: {req.outage_date}
# Outage Time: {req.outage_time} hours
# Affected Area: {req.affected_area}

# Please approve or reject here:
# http://localhost:5000/approve_general_manager/{req.id}
# """
#             )
#             mail.send(msg_gm)

#         else:
#             req.manager_approved = False

#             # Notify employee about manager rejection
#             msg_emp = Message(
#                 subject='Your Power Interruption Request - Manager Rejected',
#                 sender=app.config['MAIL_USERNAME'],
#                 recipients=[req.employee_email],
#                 body=f"""
# Hello {req.employee_name},

# Your power interruption request has been rejected by the Manager.

# Reason: {req.reason}
# Date: {req.outage_date}
# Outage Time: {req.outage_time} hours
# Affected Area: {req.affected_area}

# Please contact your manager for more details.

# Thank you.
# """
#             )
#             mail.send(msg_emp)

#         db.session.commit()
#         flash('Manager decision recorded.', 'success')
#         return redirect(url_for('submit_request'))

@app.route('/approve_manager/<int:req_id>', methods=['GET', 'POST'])
def approve_manager(req_id):
    print("🟡 Accessing /approve_manager route with ID:", req_id)

    try:
        req = PowerInterruptionRequest.query.get_or_404(req_id)
        print("🟢 Request found:", req)
    except Exception as e:
        print("🔴 Error loading request:", e)
        return "Error loading request", 500

    if request.method == 'POST':
        print("🟡 Form submitted")
        action = request.form.get('action')
        print("🟢 Action:", action)
        # Handle POST actions here...
        return "POST submitted"

    print("🟢 Rendering HTML template")
    return render_template('approve_manager.html', req=req)


@app.route('/approve_general_manager/<int:req_id>', methods=['GET', 'POST'])
def approve_general_manager(req_id):
    req = PowerInterruptionRequest.query.get_or_404(req_id)

    if request.method == 'POST':
        action = request.form['action']
        if action == 'approve':
            req.general_manager_approved = True

            # Notify employee about general manager approval
            msg_emp = Message(
                subject='Your Power Interruption Request - General Manager Approved',
                sender=app.config['MAIL_USERNAME'],
                recipients=[req.employee_email],
                body=f"""
Hello {req.employee_name},

Your power interruption request has been approved by the General Manager.

Reason: {req.reason}
Date: {req.outage_date}
Outage Time: {req.outage_time} hours
Affected Area: {req.affected_area}

Thank you.
"""
            )
            mail.send(msg_emp)

        else:
            req.general_manager_approved = False

            # Notify employee about general manager rejection
            msg_emp = Message(
                subject='Your Power Interruption Request - General Manager Rejected',
                sender=app.config['MAIL_USERNAME'],
                recipients=[req.employee_email],
                body=f"""
Hello {req.employee_name},

Your power interruption request has been rejected by the General Manager.

Reason: {req.reason}
Date: {req.outage_date}
Outage Time: {req.outage_time} hours
Affected Area: {req.affected_area}

Please contact your manager or general manager for more details.

Thank you.
"""
            )
            mail.send(msg_emp)

        db.session.commit()
        flash('General manager decision recorded.', 'success')
        return redirect(url_for('submit_request'))

    return render_template('approve_general_manager.html', req=req)

if __name__ == '__main__':
    app.run(debug=True)
