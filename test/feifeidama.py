import requests
import time
import base64, hashlib, json


class Predict(object):
    def CalcSign(self, usr_id, passwd, timestamp):
        md5 = hashlib.md5()
        md5.update((timestamp + passwd).encode("utf-8"))
        csign = md5.hexdigest()

        md5 = hashlib.md5()
        t = usr_id + timestamp + csign
        md5.update(t.encode("utf-8"))
        csign = md5.hexdigest()
        return csign

    def run(self, image_data):
        pred_type = "30500"
        user_id = "102265"
        usr_key = "ZW7NiiR3rFU+OFmIIvLltv/bnaF1md61"
        tm = str(int(time.time()))
        sign = self.CalcSign(user_id, usr_key, tm)
        asign = self.CalcSign("302465", 'UUD9ap4OU+Vo+uF2f+gk+i9QSZAw5Ywl', tm)
        img_base64 = base64.b64encode(image_data)
        param = {"user_id": "102265", "timestamp": tm, "sign": sign, "predict_type": pred_type,
                 "img_data": img_base64, "appid": "302465", "asign": asign}
        url = "http://pred.fateadm.com/api/capreg"
        try:
            rsp = requests.post(url, param)
            rep_obj = json.loads(rsp.text)
            print rep_obj
            if rep_obj['RetCode'] == '0':
                res = json.loads(rep_obj['RspData'])
                return res['result']
            else:

                time.sleep(1)
                return self.run(image_data)
        except Exception as e:
            print e
            time.sleep(1)
            return self.run(image_data)


if __name__ == '__main__':
    io = open('1.jpg', 'rb').read()
    result = Predict().run(io)
    print(result)
