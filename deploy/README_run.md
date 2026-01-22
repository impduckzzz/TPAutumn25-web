Gunicorn Django:
gunicorn -c deploy/gunicorn.conf.py

WSGI echo on 8081:
gunicorn -b 127.0.0.1:8081 deploy.wsgi_echo:application

WSGI static/dynamic on 8082:
gunicorn -b 127.0.0.1:8082 deploy.wsgi_static:application

Nginx:
sudo nginx -c $(pwd)/deploy/nginx.conf -p $(pwd)

Stop nginx:
sudo nginx -s stop -c $(pwd)/deploy/nginx.conf -p $(pwd)
