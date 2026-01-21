from flask import Flask
from controllers.applicant_controller import applicant_bp
from controllers.admin_controller import admin_bp

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.register_blueprint(applicant_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)