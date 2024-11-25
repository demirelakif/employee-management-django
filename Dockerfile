# Temel imajı seçiyoruz
FROM python:3.10.5

# Çalışma dizini ayarlıyoruz
WORKDIR /app

# Gereksinim dosyasını kopyalıyoruz ve bağımlılıkları yüklüyoruz
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# wait-for-it.sh dosyasını kopyalıyoruz
COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

# Proje dosyalarını kopyalıyoruz
COPY . /app/

# Çalışma dizinine geçiyoruz
WORKDIR /app/employee_management 

# Gerekli komutları çalıştırıyoruz
CMD ["./wait-for-it.sh", "db:5432", "--", "python", "manage.py", "runserver", "0.0.0.0:8000"]
