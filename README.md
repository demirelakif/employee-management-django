# :office_worker: Employee Management System

This project is a Django-based application developed to manage employees' leave days, working hours, and annual leave requests. The application ensures that any tardiness by an employee results in a deduction from their annual leave, based on the time difference. Additionally, it allows employees to request leave, and enables supervisors to approve or reject these requests.
## 🚀 Features

- **User Authentication:** Secure login/logout for different user roles.
- **Employee Management:** Employees can track their annual leave days and create leave requests.
- **Manager Panel:** Managers can approve or reject employee leave requests.
- **Time Management:** The system deducts annual leave hours if an employee is tardy, based on the duration of the delay.
- **Annual Leave Allocation:**  Every new employee is automatically granted 15 days of annual leave at the time of registration.

## :man_technologist: Technologies Used

<div>
	<code><img width="50" src="https://user-images.githubusercontent.com/25181517/202896760-337261ed-ee92-4979-84c4-d4b829c7355d.png" alt="Tailwind CSS" title="Tailwind CSS"/></code>
	<code><img width="50" src="https://user-images.githubusercontent.com/25181517/186711335-a3729606-5a78-4496-9a36-06efcc74f800.png" alt="Swagger" title="Swagger"/></code>
	<code><img width="50" src="https://github.com/marwin1991/profile-technology-icons/assets/62091613/9bf5650b-e534-4eae-8a26-8379d076f3b4" alt="Django" title="Django"/></code>
	<code><img width="50" src="https://user-images.githubusercontent.com/25181517/117208740-bfb78400-adf5-11eb-97bb-09072b6bedfc.png" alt="PostgreSQL" title="PostgreSQL"/></code>
	<code><img width="50" src="https://user-images.githubusercontent.com/25181517/117207330-263ba280-adf4-11eb-9b97-0ac5b40bc3be.png" alt="Docker" title="Docker"/></code>
</div>
<br/>

- **Django:** Web framework for Python.
- **PostgreSQL:** Database management.
- **Docker:** Containerization for easy deployment and scalability.
- **Bootstrap & Tailwind CSS:** For responsive and modern UI.

## 🖥️ Setup Instructions

### Clone the repository:

```bash
git clone https://github.com/username/employee-management.git
cd employee-management
````

### Install dependencies:
```bash
pip install -r requirements.txt
````

### Set up the database:
```bash
python manage.py migrate
````

### Run the server:
```bash
python manage.py runserver
````

## Docker Setup
To run the application in a Docker container:

### Run the project with Docker:
```bash
docker-compose up --build
````
Access the app at http://localhost:8000.

## API Documentation
You can explore the APIs using Swagger UI at:
```bash
http://localhost:8000/swagger/
````

## :film_strip: Screenshots

### Swagger Docs
![employee-management-swagger](https://github.com/user-attachments/assets/01e81116-77f6-41ba-8e16-a65ccb288fb8)

### Manager Panel
![employee-management_manager_dashboard](https://github.com/user-attachments/assets/3a525a0f-2c9a-4953-ad3f-b02b8876f25a)


### Employeer Home

![employee_home](https://github.com/user-attachments/assets/f2be085b-f135-4619-9f7f-77ebf0346759)


### Leave Request Panel
![employee_leave_request](https://github.com/user-attachments/assets/9f969ddb-49f8-4239-b080-77133aacd4cd)





