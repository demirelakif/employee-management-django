from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .models import Employee, AttendanceRecord, LeaveRequest, Notification
from .serializers import EmployeeSerializer,RegisterSerializer,AttendanceRecordSerializer, LeaveRequestSerializer, NotificationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

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

        # Giriş saatini kaydet
        today = datetime.now().date()
        current_time = datetime.now().time()

        attendance, created = AttendanceRecord.objects.get_or_create(
            employee=user,
            date=today,
            defaults={'first_entry': current_time}
        )
        # Eğer zaten giriş kaydı varsa sadece güncelleme yapmayız.
        if not created:
            attendance.first_entry = current_time  # Giriş saati güncellenir
            attendance.save()

        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'name': user.name,
            'attendance_id': attendance.id,
            'first_entry': attendance.first_entry,
            'last_exit': attendance.last_exit
        })


class EmployeeLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Kullanıcı ve bugünkü tarih için kaydı bul
        user = request.user
        today = datetime.now().date()
        current_time = datetime.now().time()

        try:
            attendance = AttendanceRecord.objects.get(employee=user, date=today)
            attendance.last_exit = current_time  # Çıkış saati güncellenir
            attendance.save()

            # Kullanıcının token'ını silerek oturumu sonlandırma
            request.auth.delete()

            return Response({"message": "Logout successful. Last exit time updated."})
        except AttendanceRecord.DoesNotExist:
            return Response({"error": "No attendance record found for today."}, status=400)


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
        })



class AttendanceRecordViewSet(ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)

        # Kullanıcıdan gelen `date` alanını kullanarak işlem yapıyoruz
        date = serializer.validated_data['date']
        
        # Aynı tarih ve kullanıcı için kayıt var mı kontrol ediliyor
        attendance = AttendanceRecord.objects.filter(employee=self.request.user, date=date).first()
        if not attendance:
            serializer.save(employee=self.request.user)  # Yeni kayıt oluştur
        else:
            attendance.last_exit = serializer.validated_data['last_exit']
            attendance.save()  # Mevcut kaydı güncelle





class LeaveRequestViewSet(ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Sadece kullanıcının bildirimlerini getir.
        return self.queryset.filter(user=self.request.user)
