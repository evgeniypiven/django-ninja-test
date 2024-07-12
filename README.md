# Starnavi Project

Project starnavi provides API of posts and authorization

# Configure Local Development Environment
## Requirements
1. Python 3.8.10
2. Docker
3. Windows OS

## Steps
1.Builds, (re)creates, starts, and attaches to containers for a service: 
```bash
docker-compose up -d --build
```

2.Launch migrations:
```bash
docker-compose exec web python manage.py migrate --noinput
```

3.Create admin user:
```bash
docker-compose exec web python manage.py createsuperuser
```
After all manipulations you can access admin panel by link:
```bash 
http://127.0.0.1:8000/admin
```
4.Launch all tests
```bash 
docker-compose exec web python manage.py test posts.tests
```
For using REST API, you can check Project APIs list by link:
```bash 
http://127.0.0.1:8000/api/authorization/docs
```
```bash
http://127.0.0.1:8000/api/posts/docs
```
(Most REST APIs uses Bearer token, that you can get by url /api/authorization/login)

 
When finishes your test, you can stop and remove all containers by command:
```bash
docker-compose down
```
