service nginx restart
redis-server --daemonize yes
python3 /ServerManager-Panel/manage.py runserver 0.0.0.0:8000
