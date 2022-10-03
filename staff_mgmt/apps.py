from django.apps import AppConfig


class StaffMgmtConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'staff_mgmt'

    def ready(self) -> None:
        from .signals import save_attendance_for_logged_in_user, set_department_head_end_date
        return super().ready()
