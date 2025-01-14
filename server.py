#  coding: utf-8 
import socketserver # https://docs.python.org/3.6/library/socketserver.html
from os import path # https://docs.python.org/3.6/library/os.path.html#module-os.path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# Copyright 2021 Ze Hui Peng
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# Comments follow the Google Python Style Guide:
# https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings

class MyWebServer(socketserver.BaseRequestHandler):
    def setup(self):
        """
        setup function provided by the socketserver module
        setup the responses for all the status codes
        and list the valid mime types
        """
        self.responses = {
            # first element is the content type and second element is the content
            200: 'HTTP/1.1 200 OK\r\nContent-Type: {}\r\n\r\n{}\r\n',
            # first element is the redirect address
            301: 'HTTP/1.1 301 Moved Permanently\r\nLocation: {}\r\n\r\n',
            404: 'HTTP/1.1 404 Not Found\r\n\r\n404 Error! File not found!\r\n',
            405: 'HTTP/1.1 405 Method Not Allowed\r\n\r\nThe specific request method is not allowed\r\n',
            505: 'HTTP/1.1 505 HTTP Version Not Support\r\n\r\nThe specific HTTP version is not supported\r\n'
        }

        # requirements: The webserver supports mime-types for HTML and CSS
        self.MIME_TYPES = ["css", "html"]

    def parse_data(self):
        """
        Parse the received data by decoding and splitting by lines
        and seperating each line by its ":" delimiter into key and values
        
        Returns:
            A dictionary in the following format:

            method: the HTTP request method and header (e.g. 'GET')
            path: the requested path (e.g. '/')
            protocol: the HTTP protocol (e.g. 'HTTP/1.1')
        """

        # only the first element contains useful information needed
        args = self.data.decode('utf-8').split('\r\n')[0].split(" ")
        info = {
            'method': args[0],
            # as per assignment requirement: "The webserver can serve files from ./www"
            'path': path.abspath("www") + args[1],
            'file': args[1],
            'protocol': args[2]
        }
        return info

    def get_file_content(self, file_path):
        """
        Get the content of the file by opening and reading the file
        
        Args:
            file_path: the path of the file to read
        
        Returns:
            a string that contains the content of the file
        """
        file = open(file_path, 'r')
        content = file.read()
        file.close()
        return content

    def handle(self):
        """
        handle function provided by the socketserver module
        the function will first parse the request to obtain request information,
        and provide appriate responses based on the user request
        """
        self.data = self.request.recv(4096).strip()
        if not self.data:
            return
        info = self.parse_data()
        
        # by default the response will be 404 not found error
        response = self.responses[404]

        if info["protocol"] != "HTTP/1.1":
            response = self.responses[505]
        elif info["method"] != "GET":
            response = self.responses[405]
        else:
            if path.isdir(info["path"]):
                # requirement: "Must use 301 to correct path ending"
                if not info["path"].endswith("/"):
                    response = self.responses[301].format(info["file"] + "/")
                elif path.isfile(info["path"] + "index.html"):
                    # requirement: "The webserver can return index.html from directories"
                    file_content = self.get_file_content(info["path"] + "index.html")
                    response = self.responses[200].format("text/html", file_content) 
            elif path.isfile(info["path"]):
                file_type = info["path"].split(".")[-1]
                if (file_type not in self.MIME_TYPES):
                    file_type = "application/octet-stream"
                else:
                    file_type = "text/" + file_type
                
                if path.exists(info["path"]) and "www" in path.abspath(info["path"]):
                    file_content = self.get_file_content(info["path"])
                    response = self.responses[200].format(file_type, file_content)

        self.request.sendall(response.encode('utf-8'))
    
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()