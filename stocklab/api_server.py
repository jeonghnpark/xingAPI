
from flask import Flask
from flask_core import CORS
from flask_restful import reparse, abort, Api, Resource

app=Flask(__name__)

api=Api(app)

class CodedList(Resource):
    def get(self):
        pass

class Code(Resouce):
    def get(self,code): #<string:code> 로 전달되는 인수
       pass

class Price(Resouce):
    def get(self, code):
        pass

class OrderList(Resouce):
    def get(self):
        pass

"""자원클래스와 요청 URL을 연결시켜줌, 
개별 url에 대한 get, post, put, delete는 자원 클래스의 메서드로 정의하면 
url에 대한 HTTP쵸엉을 처리할수 있음
"""


api.add_resouce(CodedList, "/codes", endpoint="codes")
api.add_resource(Code, "/codes/<string:code>", endpoint="code")

