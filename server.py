import argparse
from app import app, socketio
import os

parser = argparse.ArgumentParser(description='Run Railway Object Detection ')

parser.add_argument('--address', dest='hostname', default="localhost", help="Network interface to start the socketIO/webserver on.")
parser.add_argument('--port', dest='port', default='5000', help="Specifies the port for the socketIO/web server to start on.")
parser.add_argument('--uploads', dest='upload_path', default='uploads', help="Specifies path to store uploaded files.")

args = parser.parse_args()

hostname = os.environ.get('ROD_HOSTNAME', args.hostname)
port = os.environ.get('ROD_PORT', args.port)
upload_path = os.environ.get('ROD_UPLOADS', args.upload_path)

os.environ['ROD_HOSTNAME'] = hostname
os.environ['ROD_PORT'] = port
os.environ['ROD_UPLOADS'] = upload_path

socketio.run(app, host = hostname, port = port)