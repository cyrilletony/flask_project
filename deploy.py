from gevent.pywsgi import WSGIServer
import socket
from app import app

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

print("\nConnect to this System on: http://{}:5000\n".format(ip))

http_server = WSGIServer((ip, 5000), app)
http_server.serve_forever()