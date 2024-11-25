from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from core.models import Employee, AttendanceRecord, LeaveRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from rest_framework.authtoken.models import Token

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('/')  # Başarılı girişte dashboard yönlendirme
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        name = request.POST.get("name")

        # Kullanıcıyı oluştur
        user = Employee.objects.create_user(
            username=username, password=password, name=name
        )
        return redirect('login')  # Başarılı kayıt sonrası login ekranına yönlendirme

    return render(request, "register.html")


@login_required
def home_view(request):
    """
    Kullanıcının ana sayfası. Kullanıcının yıllık izin bilgilerini, katılım kayıtlarını ve rolünü gösterir.
    """
    user = request.user


    if(user.is_manager):
        selected_date = request.GET.get('date', None)
        leave_requests = LeaveRequest.objects.all()
        attendances = AttendanceRecord.objects.all()
        if selected_date:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            leave_requests = leave_requests.filter(start_date__lte=selected_date, end_date__gte=selected_date)
            attendances = attendances.filter(date=selected_date)
        context = {
            "attendances": attendances,
            "leave_requests": leave_requests
        }
    else:
        attendances = AttendanceRecord.objects.filter(employee=user)
        annual_leave_days = user.annual_leave_days
        leave_requests = LeaveRequest.objects.filter(employee=request.user)
        context = {
            "annual_leave_days": annual_leave_days,
            "attendances": attendances,
            "leave_requests": leave_requests
        }




    # Eğer kullanıcı bir yönetici ise, yönetici sayfasına yönlendirme yapabilir
    if user.is_manager:
        return render(request, "manager_dashboard.html", context)

    return render(request, "home.html", context)


@login_required
def leave_request(request):
    """
    Kullanıcı izin talebi oluşturma sayfası.
    """
    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        reason = request.POST.get("reason")

        # İzin talebi oluştur
        LeaveRequest.objects.create(
            employee=request.user,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )
        messages.success(request, "Leave request submitted successfully!")
        return redirect('home')

    return render(request, "leave_request.html")
