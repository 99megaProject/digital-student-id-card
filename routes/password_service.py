from flask import Blueprint ,jsonify, request,url_for ,render_template_string 
from werkzeug.security import generate_password_hash, check_password_hash
import json
import sys
import os 
 
import jwt
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db_connection import get_collection
from utils.email_service import send_email


password_service_bp = Blueprint('password_service', __name__, url_prefix='')
JWT_SECRET = "jwt_super_secret_key"

reset_password_html = '''
<h2>Reset Password</h2>
<form method="POST">
  New Password: <input type="password" name="password" required>
  Confirm Password: <input type="password" name="confirm_password" required>
  <input type="submit" value="Reset Password">
</form>
'''

def generate_reset_email_body(user_name, reset_link):
    return f"""
    Hi {user_name},

    We received a request to reset your password. Click the link below to set a new password. This link will expire in 30 minutes:

    {reset_link}

    If you did not request this, please ignore this email — your password will remain unchanged.

    Thanks,
    Digital Student ID Card Team
    """



@password_service_bp.route('/forgot-password' ,methods=['POST'])
def forgot_password():

    user_type = request.form.get('user_type')

    print("user type" , user_type)
    if user_type=="student" :
        try:
            roll_no = request.form.get('roll_no')
            registration_no = request.form.get('registration_no')
            print(roll_no,registration_no)

            # Validate input
            if not roll_no and not registration_no:
                return jsonify({"error": "Please provide either roll_no or registration_no"}), 400

            # Get collection
            student_collection = get_collection('student')

            # Build query
            query = {}
            token_query = str(roll_no)
            token_credentail_flage = "roll_no"
            if roll_no:
                query['roll_no'] = int( roll_no)
            elif registration_no:
                query['registration_no'] = registration_no
                token_query = registration_no
                token_credentail_flage = "registration_no"


            # Fetch student
            student = student_collection.find_one(query)

            if not student:
                return jsonify({"message": "Student not found"}), 404

            # Convert ObjectId to string
            student['_id'] = str(student['_id'])


            token = generate_reset_token(token_query)
            reset_link = url_for("password_service.reset_password", token=token,type="student" , credentail_type=token_credentail_flage, _external=True)
            # For demo: print link. In production, send via email.
            print(f"""Password reset link for {student.get("email")}: {reset_link}""")

            send_email(
                subject="Digital ID card — Password Reset Request",
                body=generate_reset_email_body(student["name"],reset_link),

                receiver_email=student.get("email"),
            )

            return jsonify({
                "message": f"""Password reset link is sent to {student.get("email")}""",
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else :
        try:
            name =  request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')

            print(email ,phone)

            # Validate input
            if not name:
                return jsonify({"error": "Please provide name."}), 400
            elif not (email or phone):
                return jsonify({"error": "Please provide either an email or a phone number."}), 400

            # Get collection
            teacher_collection = get_collection('teacher')

            # Build query
            query = { "name": { "$regex": f"^{name}$", "$options": "i" } }
            # query = {}
            if email:
                query['email'] = email
            elif phone:
                query['phone'] = int(phone)


            teacher = teacher_collection.find_one(query)

            if not teacher:
                return jsonify({"message": "Teacher not found"}), 404

            token_query = email
            token_credentail_flage = "email"
            if phone : 
                token_query = str(phone)
                token_credentail_flage = "phone"

            token = generate_reset_token(token_query)
            reset_link = url_for("password_service.reset_password", token=token, type="teacher" , credentail_type=token_credentail_flage, _external=True)
            # For demo: print link. In production, send via email.
            print(f"""Password reset link for {teacher.get("email")}: {reset_link}""")

            send_email(
                subject="Digital ID card — Password Reset Request",
                body=generate_reset_email_body(teacher["name"],reset_link),

                receiver_email=teacher.get("email"),
            )

            return jsonify({
                "message": f"""Password reset link is sent to {teacher.get("email")}""",
            }), 200


        except Exception as e:
            return jsonify({"error": str(e)}), 500



@password_service_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token")
    user_type = request.args.get("type")
    credentail_type = request.args.get("credentail_type")

    if not token:
        return jsonify({"status": "Failed", "message": "Token not found"}), 404
    
    credentail = verify_reset_token(token)

    print(token,user_type,credentail,credentail_type)
    if not credentail:
        return jsonify({"status": "Failed", "message": "Invalid or expired token!"}), 404

    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password:
            return jsonify({"status": "Failed", "message": "Passwords not matched."}), 400
        else:
            hashed_password = generate_password_hash(password)
            print(hashed_password)
            collection = {}
            if user_type == "student":
                collection = get_collection('student')
            else : collection = get_collection('teacher')

            if credentail_type=="roll_no" or credentail_type=="phone":
                credentail = int(credentail)

            collection.update_one(
                {credentail_type: credentail},
                {"$set": {"password": hashed_password}}
            )
           
            return jsonify({"status": "Success", "message": "Password reset successfully!"}), 200
            

    return render_template_string(reset_password_html)


# ----------------------
# Helper Functions
# ----------------------
def generate_reset_token(credentail):
    payload = {
        "credentail": credentail,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # 30 min expiry
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token

def verify_reset_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload["credentail"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ----------------------
# Routes
# ----------------------
# @app.route("/", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email = request.form["email"]
#         password = request.form["password"]
#         user = users_collection.find_one({"email": email})
#         if user and check_password_hash(user["password"], password):
#             return f"Logged in as {email}!"
#         else:
#             flash("Invalid credentials")
#     return render_template_string(login_html)

# @app.route("/forgot-password", methods=["GET", "POST"])
# def forgot_password():

#     user_type = request.form.get('user_type')

#     if user_type=="studenet" :
#         pass
#     else :
#         pass

#     if request.method == "POST":
#         email = request.form["email"]
#         user = users_collection.find_one({"email": email})
#         if user:
#             token = generate_reset_token(email)
#             reset_link = url_for("reset_password", token=token, _external=True)
#             # For demo: print link. In production, send via email.
#             print(f"Password reset link for {email}: {reset_link}")
#         flash("If the email exists, a reset link has been sent.")
#     return render_template_string(forgot_password_html)

# @app.route("/reset-password", methods=["GET", "POST"])
# def reset_password():
#     token = request.args.get("token")
#     if not token:
#         return "Missing token!"
    
#     email = verify_reset_token(token)
#     if not email:
#         return "Invalid or expired token!"

#     if request.method == "POST":
#         password = request.form["password"]
#         confirm_password = request.form["confirm_password"]
#         if password != confirm_password:
#             flash("Passwords do not match!")
#         else:
#             hashed_password = generate_password_hash(password)
#             users_collection.update_one(
#                 {"email": email},
#                 {"$set": {"password": hashed_password}}
#             )
#             flash("Password reset successfully!")
#             return redirect(url_for("login"))

#     return render_template_string(reset_password_html)

# # ----------------------
# # Run App
# # ----------------------
# if __name__ == "__main__":
#     # Create a test user if not exists
#     if not users_collection.find_one({"email": "user@example.com"}):
#         users_collection.insert_one({
#             "email": "user@example.com",
#             "password": generate_password_hash("password123")
#         })
#     app.run(debug=True)
