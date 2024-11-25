from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models



class EmployeeManager(BaseUserManager):
    def create_user(self, username, password=None, name=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        user = self.model(username=username, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, name=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, password, name, **extra_fields)

class Employee(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # AbstractBaseUser'da zaten var
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    annual_leave_days = models.FloatField(default=15)


    groups = models.ManyToManyField(
        'auth.Group',
        related_name='employee_groups',  # Çakışmayı önlemek için özel bir isim
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='employee_permissions',  # Çakışmayı önlemek için özel bir isim
        blank=True
    )

    objects = EmployeeManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.username




class AttendanceRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()  # Artık dışarıdan alınabilir
    first_entry = models.TimeField()
    last_exit = models.TimeField(null=True, blank=True)
    penalty_minutes = models.FloatField(default=0)  # Geç kalınan dakika

    class Meta:
        unique_together = ('employee', 'date')  # Her kullanıcı için bir günlük kayıt


class LeaveRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=(('pending', 'Beklemede'), ('approved', 'Onaylandı'), ('rejected', 'Reddedildi')),
        default='pending'
    )
    requested_on = models.DateTimeField(auto_now_add=True)  # Talep zamanı


class Notification(models.Model):
    Employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Bildirim alacak kişi
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Bildirim oluşturulma zamanı
    is_read = models.BooleanField(default=False)  # Okunup okunmadığı bilgisi




