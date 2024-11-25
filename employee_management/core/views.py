from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .models import Employee, AttendanceRecord, LeaveRequest
from .serializers import EmployeeSerializer,RegisterSerializer,AttendanceRecordSerializer, LeaveRequestSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from django.contrib.auth import logout
from django.contrib.sessions.backends.db import SessionStore

def is_holiday(date):
    return date.weekday() >= 5  # Cumartesi (5) ve Pazar (6)

from rest_framework.exceptions import ValidationError
from datetime import datetime

class EmployeeAuthToken(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise AuthenticationFailed("Invalid credentials or inactive account")

        # Token oluştur veya mevcut olanı getir
        token, created = Token.objects.get_or_create(user=user)
        request.session['auth_token'] = token.key
        login(request, user)  # Django'nun oturumunu başlat

        # İstekten manuel olarak tarih ve saat alma
        date_str = request.data.get('date')
        time_str = request.data.get('time')

        # Tarih ve saat doğrulama
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
            time = datetime.strptime(time_str, "%H:%M:%S").time() if time_str else datetime.now().time()
        except ValueError:
            raise ValidationError("Invalid date or time format. Use 'YYYY-MM-DD' for date and 'HH:MM:SS' for time.")

        # Tatil kontrolü
        if is_holiday(date):
            return Response({
                'message': f"{date} is a holiday. Attendance will not be recorded.",
                'annual_leave_days': user.annual_leave_days
            }, status=status.HTTP_200_OK)

        
        # Çalışma saatlerini kontrol et
        company_start = datetime.strptime("08:00:00", "%H:%M:%S").time()
        company_end = datetime.strptime("18:00:00", "%H:%M:%S").time()
        
        
        # Attendance kaydı  
        attendance, created = AttendanceRecord.objects.get_or_create(
            employee=user,
            date=date,
            defaults={'first_entry': time}
        )
        

        if(created):
        
            if attendance.first_entry > company_start and attendance.first_entry < company_end:
                late_minutes = (datetime.combine(date, attendance.first_entry) - datetime.combine(date, company_start)).seconds / 60
                user.annual_leave_days -= late_minutes / 60 / 10  # Saat üzerinden gün olarak düş
                user.save()
                attendance.penalty_minutes += late_minutes 
                attendance.save()

        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'name': user.name,
            'attendance_id': attendance.id,
            'first_entry': attendance.first_entry,
            'last_exit': attendance.last_exit,
            'message': 'Attendance already created.' if not created else 'Attendance created.'
        })



class EmployeeLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

         # İstekten manuel olarak tarih ve saat alma
        date_str = request.data.get('date')
        time_str = request.data.get('time')

        # Tarih ve saat doğrulama
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
            time = datetime.strptime(time_str, "%H:%M:%S").time() if time_str else datetime.now().time()
        except ValueError:
            raise ValidationError("Invalid date or time format. Use 'YYYY-MM-DD' for date and 'HH:MM:SS' for time.")

        try:
            # O günkü kaydı getir
            attendance = AttendanceRecord.objects.get(employee=user, date=date)
            company_start = datetime.strptime("08:00:00", "%H:%M:%S").time()
            company_end = datetime.strptime("18:00:00", "%H:%M:%S").time()

            # Erken çıkış için hesaplama
            if time < company_end:
                early_exit_minutes = (datetime.combine(date, company_end) - datetime.combine(date, time)).seconds / 60
                user.annual_leave_days -= early_exit_minutes / 60 / 10  # Saat üzerinden gün olarak düş
                attendance.penalty_minutes += early_exit_minutes
                attendance.save()
                user.save()
            
            if attendance.last_exit is not None:
                # Eğer çıkış zaten yapılmışsa hata dön
                return Response({
                    "error": "Last exit for today is already recorded.",
                    "attendance_id": attendance.id,
                    "first_entry": attendance.first_entry,
                    "last_exit": attendance.last_exit
                }, status=200)

            # Çıkış kaydı yap
            attendance.last_exit = time_str
            attendance.save()

            # Token silme işlemi
            request.auth.delete()

            # Django session'u temizleme
            logout(request)
            request.session.flush()

            return Response({
                "message": "Logout successful. Last exit time recorded.",
                "attendance_id": attendance.id,
                "first_entry": attendance.first_entry,
                "last_exit": attendance.last_exit
            },status=200)
        except AttendanceRecord.DoesNotExist:
            return Response({"error": "No attendance record found for today."}, status=200)


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully!",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "username": user.username
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeApi(APIView): 
    permission_classes = [IsAuthenticated]  # only authenticated users can access this view
    def get(self, request):
        queryset = Employee.objects.all()
        serializer = EmployeeSerializer(queryset,many=True)
        return Response({
            "status": True,
            "data": serializer.data
        },status=200)





class AttendanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Eğer kullanıcı bir manager değilse sadece kendi attendance kayıtlarını getirir.
        Manager'lar ise tüm kayıtları görebilir.
        """
        user = self.request.user
        
        if user.is_manager:
            # Eğer kullanıcı bir manager ise, tüm attendance kayıtlarını getir
            return AttendanceRecord.objects.all()
        else:
            # Eğer kullanıcı bir manager değilse, sadece kendi attendance kayıtlarını getir
            return AttendanceRecord.objects.filter(employee=user)
    
    def perform_create(self, serializer):
        # Perform create fonksiyonunda aynı mantık
        serializer.is_valid(raise_exception=True)
        date = serializer.validated_data['date']
        
        # Kullanıcı için aynı tarihli bir attendance kaydı olup olmadığını kontrol et
        attendance = AttendanceRecord.objects.filter(employee=self.request.user, date=date).first()
        if not attendance:
            serializer.save(employee=self.request.user)  # Yeni kayıt oluştur
        else:
            # Eğer daha önce giriş yapılmışsa, çıkış saatini güncelle
            attendance.last_exit = serializer.validated_data['last_exit']
            attendance.save()



from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.views import APIView
from .models import LeaveRequest
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .tasks import notify_manager  # Celery görevi

class LeaveRequestViewSet(ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        print("buraya girdi")
        if user.is_manager:
            # Yöneticiler tüm talepleri görebilir
            return LeaveRequest.objects.all()
        else:
            # Çalışanlar yalnızca kendi taleplerini görebilir
            
            return LeaveRequest.objects.filter(employee=user)

    def perform_create(self, serializer):
        """
        İzin talebi oluşturulduğunda, kullanıcı otomatik olarak çalışan olarak atanır.
        Ayrıca yöneticilere bildirim gönderir.
        """
        user = self.request.user
        if user.annual_leave_days < (serializer.validated_data['end_date'] - serializer.validated_data['start_date']).days + 1:
            raise ValueError("Yıllık izin gün sayısı yeterli değil.")
        
        leave_request = serializer.save(employee=user)

        # Celery ile yöneticilere bildirim gönder
        notify_manager.delay(
            leave_request_id=leave_request.id,
            employee_name=user.name,
            reason=leave_request.reason
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve_leave_request(self, request, pk=None):
        """
        İzin talebini onayla
        """
        leave_request = get_object_or_404(LeaveRequest, pk=pk)

        # Yalnızca yöneticilerin onaylayabileceği talepler
        if not request.user.is_manager:
            return Response({"detail": "You do not have permission to approve leave requests."}, status=status.HTTP_403_FORBIDDEN)

        if leave_request.status == "approved":
            return Response({"detail": "Leave request already approved."}, status=status.HTTP_400_BAD_REQUEST)

        # Talebin durumunu onayla olarak güncelle
        leave_request.status = "approved"
        leave_request.save()

        # Celery ile yöneticilere bildirim gönder
        notify_manager.delay(
            leave_request_id=leave_request.id,
            employee_name=leave_request.employee.name,
            reason=leave_request.reason
        )

        return Response({"detail": "Leave request approved."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject_leave_request(self, request, pk=None):
        """
        İzin talebini reddet
        """
        leave_request = get_object_or_404(LeaveRequest, pk=pk)

        # Yalnızca yöneticilerin reddedebileceği talepler
        if not request.user.is_manager:
            return Response({"detail": "You do not have permission to reject leave requests."}, status=status.HTTP_403_FORBIDDEN)

        if leave_request.status == "rejected":
            return Response({"detail": "Leave request already rejected."}, status=status.HTTP_400_BAD_REQUEST)

        # Talebin durumunu reddedildi olarak güncelle
        leave_request.status = "rejected"
        leave_request.save()

        # Celery ile yöneticilere bildirim gönder
        notify_manager.delay(
            leave_request_id=leave_request.id,
            employee_name=leave_request.employee.name,
            reason=leave_request.reason
        )

        return Response({"detail": "Leave request rejected."}, status=status.HTTP_200_OK)

