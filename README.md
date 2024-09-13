# Django Ninja Test Project

Project django ninja test provides API of posts and authorization

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
5. Launch enable auto reply for post. For this task firstly you have to build or launch redis container. After that,
through next command you have to launch celery worker:
```bash 
docker-compose exec web celery -A django_ninja_test.celery_app worker --loglevel=INFO -P solo
```
After launch worker, you can launch enable auto reply through request:
```bash 
http://127.0.0.1:8000/api/posts/enable-auto-reply/{post_id}
```
In previous request you have to pass:
    Bearer token - token of authorization;
    hours - task delay attribute in request json body;
    post_id - id of specific post

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
