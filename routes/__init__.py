from .admin_route import admin_bp
from .student_route import student_bp
from .password_service import password_service_bp
from .teacher_route import teacher_bp
# A list of all blueprints to register
all_blueprints = [ student_bp, admin_bp, teacher_bp, password_service_bp]
