mkdir -p bench
python -c "import os;os.makedirs('static',exist_ok=True);open('static/sample.html','wb').write(b'a'*20000)" 
gunicorn -c deploy/gunicorn.conf.py ask_yuntsevich.wsgi:application &
G1=$!
gunicorn -b 127.0.0.1:8081 deploy.wsgi_echo:application &
G2=$!
gunicorn -b 127.0.0.1:8082 deploy.wsgi_static:application &
G3=$!
sleep 1
ab -n 2000 -c 50 http://127.0.0.1/sample.html > bench/01_nginx_static.txt
ab -n 2000 -c 50 http://127.0.0.1:8082/sample.html > bench/02_gunicorn_static.txt
ab -n 2000 -c 50 http://127.0.0.1:8081/?a=1 > bench/03_gunicorn_dynamic.txt
ab -n 2000 -c 50 http://127.0.0.1/?a=1 > bench/04_nginx_proxy_dynamic_nocache.txt
ab -n 2000 -c 50 http://127.0.0.1/?a=1 > bench/05_nginx_proxy_dynamic_cache.txt
kill $G1 $G2 $G3
