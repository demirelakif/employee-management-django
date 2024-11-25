from rest_framework import serializers
from .models import Employee, AttendanceRecord, LeaveRequest

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'username', 'name', 'is_manager', 'annual_leave_days']



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = Employee
        fields = ['name', 'username', 'password']

    def create(self, validated_data):
        user = Employee(
            name=validated_data['name'],
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])  # Şifre hashlenir
        user.save()
        return user




class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = ['date', 'first_entry', 'last_exit', 'penalty_minutes','employee']
        read_only_fields = ['penalty_minutes']  # Geç kalınan dakika sunucu tarafından hesaplanacak


class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['id', 'start_date', 'end_date', 'reason', 'status', 'requested_on']

