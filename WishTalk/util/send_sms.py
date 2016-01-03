# -*- coding: utf-8 -*-
import top.api
from config import SMS_APPID, SMS_APPKEY
def send_sms_checkcode(phone, code):
    req= top.api.AlibabaAliqinFcSmsNumSendRequest()
    req.set_app_info(top.appinfo(SMS_APPID, SMS_APPKEY))

    req.sms_type = "normal"
    req.sms_free_sign_name = "注册验证"
    req.sms_param = "{\"code\":\"%s\",\"product\":\"心愿说\"}" % str(code)
    req.rec_num = str(phone)
    req.sms_template_code = "SMS_3055518"
    try:
        resp = req.getResponse()
        #{u'alibaba_aliqin_fc_sms_num_send_response': {u'result': {u'model': u'100374878567^1100693791827', u'success': True, u'err_code': u'0'}, u'request_id': u'zddgbg3a1u6s'}}
        if resp["alibaba_aliqin_fc_sms_num_send_response"]["result"]["success"]:
            return True
        else:
            return False
    except Exception,e:
        print(e)
        return False

def send_sms_forget_code(phone, code):
    req = top.api.AlibabaAliqinFcSmsNumSendRequest()
    req.set_app_info(top.appinfo(SMS_APPID, SMS_APPKEY))

    req.sms_type = "normal"
    req.sms_free_sign_name = "身份验证"
    req.sms_param = "{\"code\":\"%s\",\"product\":\"心愿说\"}" % str(code)
    req.rec_num = str(phone)
    req.sms_template_code = "SMS_3055516"
    try:
        resp = req.getResponse()
        #{u'alibaba_aliqin_fc_sms_num_send_response': {u'result': {u'model': u'100374878567^1100693791827', u'success': True, u'err_code': u'0'}, u'request_id': u'zddgbg3a1u6s'}}
        if resp["alibaba_aliqin_fc_sms_num_send_response"]["result"]["success"]:
            return True
        else:
            return False
    except Exception,e:
        print(e)
        return False

#send_sms_checkcode("12345678901", "1234")