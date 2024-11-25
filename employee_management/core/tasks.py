from celery import shared_task
from .models import LeaveRequest, Employee, Notification

@shared_task
def notify_manager(leave_request_id, employee_name, reason):
    """
    Yöneticilere izin talebi bildirimi gönderir.
    """
    leave_request = LeaveRequest.objects.get(id=leave_request_id)
    managers = Employee.objects.filter(is_manager=True)

    for manager in managers:
        Notification.objects.create(
            user=manager,
            message=f"{employee_name} bir izin talebinde bulundu.\nSebep: {reason}",
            link=f"/manager/leave-requests/{leave_request_id}/"  # Talep detayına giden link
        )
