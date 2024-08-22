uwsgi --ini /conf/uwsgi.ini &

exec daphne -b 0.0.0.0 -p 8002 core.asgi:application
