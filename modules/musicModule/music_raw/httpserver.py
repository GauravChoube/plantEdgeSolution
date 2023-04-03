from logging import root
from flask import Flask, Response, abort, request


class EndpointAction(object):

    def __init__(self, action):
        self.action = action

    def __call__(self, *args):
        # Perform the action
        resp,header,code = self.action()
        # Send it
        if code == 204:
            return Response(status=code,headers=header)
        else:
            return Response(resp, status=code, headers=header)

def root():
        header = {"Content-Type": "text/plain"}
        return "I am root ! How May I help?",header,200


class HTTP_Sever():
    pass

    def __init__(self, name,hostAdddress = '0.0.0.0',portAddress="8080",debugFlag = False):
        self.app = Flask(name)
        self.address = hostAdddress
        self.port = portAddress
        self.debugflag = debugFlag

        self.app.add_url_rule(rule='/', endpoint='root',view_func = EndpointAction(root),methods=['POST','GET'])


    def run(self):
        self.app.run(host=self.address, port= self.port, debug =self.debugflag,threaded=True)


    def add_endpoint(self, rule=None, endpoint=None, handler=None, method=['POST']):
        self.app.add_url_rule(rule, endpoint, view_func= EndpointAction(handler),methods=method)
    
    def sendResponse(self,code =400, data = 'Not found',header = None):
        '''
        send data back to same client request based X-Ms-client-Request-id
        '''
        # Create the answer (bundle it in a correctly formatted HTTP answer)
        self.response = Response(data, status=code, headers=header)
        return self.response