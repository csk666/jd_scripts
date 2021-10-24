#!/bin/env python3
# -*- coding: utf-8 -*
'''
cron: 5 0 0 * * * jd_khc.py
new Env('京手机狂欢城只助力');
'''

# export jd818_pins=["pt_pin1","pt_pin2"]

from urllib.parse import unquote, quote
import time, datetime, os, sys
import requests, json, re, random
import threading

UserAgent = ''
script_name = '手机狂欢城只助力'


def printT(msg):
    print("[{}]: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))
    sys.stdout.flush()


def delEnvs(label):
    try:
        if label == 'True' or label == 'yes' or label == 'true' or label == 'Yes':
            return True
        elif label == 'False' or label == 'no' or label == 'false' or label == 'No':
            return False
    except:
        pass
    try:
        if '.' in label:
            return float(label)
        elif '&' in label:
            return label.split('&')
        elif '@' in label:
            return label.split('@')
        else:
            return int(label)
    except:
        return label


class getJDCookie():
    # 适配青龙平台环境ck
    def getckfile(self):
        ql_new = '/ql/config/env.sh'
        ql_old = '/ql/config/cookie.sh'
        if os.path.exists(ql_new):
            printT("当前环境青龙面板新版")
            return ql_new
        elif os.path.exists(ql_old):
            printT("当前环境青龙面板旧版")
            return ql_old

    # 获取cookie
    def getallCookie(self):
        cookies = ''
        ckfile = self.getckfile()
        try:
            if os.path.exists(ckfile):
                with open(ckfile, "r", encoding="utf-8") as f:
                    cks_text = f.read()
                if 'pt_key=' in cks_text and 'pt_pin=' in cks_text:
                    r = re.compile(r"pt_key=.*?pt_pin=.*?;", re.M | re.S | re.I)
                    cks_list = r.findall(cks_text)
                    if len(cks_list) > 0:
                        for ck in cks_list:
                            cookies += ck
            return cookies
        except Exception as e:
            printT(f"【getCookie Error】{e}")

    # 检测cookie格式是否正确
    def getUserInfo(self, ck, user_order, pinName):
        url = 'https://me-api.jd.com/user_new/info/GetJDUserInfoUnion?orgFlag=JD_PinGou_New&callSource=mainorder&channel=4&isHomewhite=0&sceneval=2&sceneval=2&callback='
        headers = {
            'Cookie': ck,
            'Accept': '*/*',
            'Connection': 'close',
            'Referer': 'https://home.m.jd.com/myJd/home.action',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 'me-api.jd.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Mobile/15E148 Safari/604.1',
            'Accept-Language': 'zh-cn'
        }
        try:
            resp = requests.get(url=url, headers=headers, timeout=60).json()
            if resp['retcode'] == "0":
                nickname = resp['data']['userInfo']['baseInfo']['nickname']
                return ck, nickname
            else:
                context = f"账号{user_order}【{pinName}】Cookie 已失效！请重新获取。"
                print(context)
                return ck, False
        except Exception:
            context = f"账号{user_order}【{pinName}】Cookie 已失效！请重新获取。"
            print(context)
            return ck, False

    def getcookies(self):
        """
        :return: cookiesList,userNameList,pinNameList
        """
        cookiesList = []
        pinNameList = []
        nickNameList = []
        cookies = self.getallCookie()
        if 'pt_key=' in cookies and 'pt_pin=' in cookies:
            r = re.compile(r"pt_key=.*?pt_pin=.*?;", re.M | re.S | re.I)
            result = r.findall(cookies)
            if len(result) >= 1:
                printT("您已配置{}个账号".format(len(result)))
                user_order = 1
                for ck in result:
                    r = re.compile(r"pt_pin=(.*?);")
                    pinName = r.findall(ck)
                    pinName = unquote(pinName[0])
                    # 获取账号名
                    ck, nickname = self.getUserInfo(ck, user_order, pinName)
                    if nickname != False:
                        cookiesList.append(ck)
                        pinNameList.append(pinName)
                        nickNameList.append(nickname)
                        user_order += 1
                    else:
                        user_order += 1
                        continue
                if len(cookiesList) > 0:
                    return cookiesList, pinNameList, nickNameList
                else:
                    printT("没有可用Cookie，已退出")
                    exit(4)
        else:
            printT("没有可用Cookie，已退出")
            exit(4)


def getPinEnvs():
    if "jd818_pins" in os.environ:
        if len(os.environ["jd818_pins"]) != 0:
            jd818_pins = os.environ["jd818_pins"]
            jd818_pins = jd818_pins.replace('[', '').replace(']', '').replace('\'', '').replace(' ', '').split(',')
            printT(f"已获取并使用Env环境 jd818_pins:{jd818_pins}")
            return jd818_pins
        else:
            printT('请先配置export jd818_pins=["pt_pin1","pt_pin2"]')
            exit(4)
    printT('请先配置export jd818_pins=["pt_pin1","pt_pin2"]')
    exit(4)

# 随机UA
def userAgent():
    """
    随机生成一个UA
    :return: jdapp;iPhone;9.4.8;14.3;xxxx;network/wifi;ADID/201EDE7F-5111-49E8-9F0D-CCF9677CD6FE;supportApplePay/0;hasUPPay/0;hasOCPay/0;model/iPhone13,4;addressid/2455696156;supportBestPay/0;appBuild/167629;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1
    """
    if not UserAgent:
        uuid = ''.join(random.sample('123456789abcdef123456789abcdef123456789abcdef123456789abcdef', 40))
        addressid = ''.join(random.sample('1234567898647', 10))
        iosVer = ''.join(
            random.sample(["14.5.1", "14.4", "14.3", "14.2", "14.1", "14.0.1", "13.7", "13.1.2", "13.1.1"], 1))
        iosV = iosVer.replace('.', '_')
        iPhone = ''.join(random.sample(["8", "9", "10", "11", "12", "13"], 1))
        ADID = ''.join(random.sample('0987654321ABCDEF', 8)) + '-' + ''.join(
            random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(
            random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(random.sample('0987654321ABCDEF', 12))

        return f'jdapp;iPhone;10.0.4;{iosVer};{uuid};network/wifi;ADID/{ADID};supportApplePay/0;hasUPPay/0;hasOCPay/0;model/iPhone{iPhone},1;addressid/{addressid};supportBestPay/0;appBuild/167629;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS {iosV} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1'
    else:
        return UserAgent


# 设置请求头
def setHeaders(cookie):
    headers = {
        "Host": "api.m.jd.com",
        "cookie": cookie,
        "charset": "UTF-8",
        "accept-encoding": "br,gzip,deflate",
        "user-agent": "okhttp/3.12.1;jdmall;android;version/10.0.8;build/89053;screen/1080x2029;os/10;network/wifi;",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded; charset\u003dUTF-8",
        "content-length": "48"
    }
    return headers


# 获取邀请码
def share(my_cookie,nickname):
    url = 'https://api.m.jd.com/api'
    UA = userAgent()
    headers = {
        "Host": "api.m.jd.com",
        "content-length": "172",
        "accept": "application/json, text/plain, */*",
        "origin": "https://carnivalcity.m.jd.com",
        "user-agent": UA,
        "content-type": "application/x-www-form-urlencoded",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "referer": "https://carnivalcity.m.jd.com/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q\u003d0.9,en-US;q\u003d0.8,en;q\u003d0.7",
        "cookie": '__jda=122270672.16284882664002016987922.1628488266.1628488266.1628488266.1;__jdv=122270672%7Cdirect%7C-%7Cnone%7C-%7C1628488266402;__jdc=122270672;mba_muid=16284882664002016987922;shshshfp=234de4b0aaf7878e76554af3039eb9bf;shshshfpa=272e547b-5c97-7432-1824-d57611a4d6c0-1628488270;shshshsID=05805da17d23190f51d015bfcf67bec0_1_1628488270685;shshshfpb=yRz6zg0dJIS8Po%2FeQ8YxeKA%3D%3D;3AB9D23F7A4B3C9B=EZRC2BS2B3U7XTFLUKTSJVGTXYSC22EIBN2GGZSBLIAIW2O5BYCUSHYIJHHP3A63YKIGF4FSAR5YQHKL4BJYM3CL3M;TrackerID=5i6KmNXbP7za8nPJKlCI45N31ediuZDET5-Soy1IpGGJzm6d9N4hWitYLfYVMb07FN9xwYBsDsKtqdd5ujji6pl0sDJPSLm29fN89vagDU51RlhC8rgKWhLKScODUxIq;' + my_cookie + ';pt_token=oss1b9v6;__jdb=122270672.3.16284882664002016987922|1.1628488266;mba_sid=16284882664066635066110123546.3;__jd_ref_cls=carnivalcity_1616135996494%7C41'
    }
    body = json.dumps({"apiMapping": "/khc/task/getSupport"})
    data = {
        'appid': 'guardian-starjd',
        'functionId': 'carnivalcity_jd_prod',
        'body': body,
        't': '1628488283504',
        'loginType': '2',
        'loginWQBiz': 'rdcactivity'
    }
    res = requests.post(url=url, headers=headers, data=data).json()
    # print(res)
    if res['code'] == 200:
        # print(res['data']['shareId'])
        return (res['data']['shareId'])
    elif res['code'] == 1002:
        print(nickname+'是黑号')
        return '-1'

# 助力好友
def help(mycookie,nickname,cookiesList,nickNameList):
    shareId = share(mycookie,nickname)
    if shareId != '-1':
        UA = userAgent()
        url = 'https://api.m.jd.com/api'
        body = json.dumps({"shareId": shareId, "apiMapping": "/khc/task/doSupport"})
        data = {
            'appid': 'guardian-starjd',
            'functionId': 'carnivalcity_jd_prod',
            'body': body,
            't': '1628488283504',
            'loginType': '2',
            'loginWQBiz': 'rdcactivity'
        }
        for i in range(len(cookiesList)):
            headers = {
                "Host": "api.m.jd.com",
                "content-length": "172",
                "accept": "application/json, text/plain, */*",
                "origin": "https://carnivalcity.m.jd.com",
                "user-agent": UA,
                "content-type": "application/x-www-form-urlencoded",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "referer": "https://carnivalcity.m.jd.com/",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "zh-CN,zh;q\u003d0.9,en-US;q\u003d0.8,en;q\u003d0.7",
                "cookie": '__jda=122270672.16284882664002016987922.1628488266.1628488266.1628488266.1;__jdv=122270672%7Cdirect%7C-%7Cnone%7C-%7C1628488266402;__jdc=122270672;mba_muid=16284882664002016987922;shshshfp=234de4b0aaf7878e76554af3039eb9bf;shshshfpa=272e547b-5c97-7432-1824-d57611a4d6c0-1628488270;shshshsID=05805da17d23190f51d015bfcf67bec0_1_1628488270685;shshshfpb=yRz6zg0dJIS8Po%2FeQ8YxeKA%3D%3D;3AB9D23F7A4B3C9B=EZRC2BS2B3U7XTFLUKTSJVGTXYSC22EIBN2GGZSBLIAIW2O5BYCUSHYIJHHP3A63YKIGF4FSAR5YQHKL4BJYM3CL3M;TrackerID=5i6KmNXbP7za8nPJKlCI45N31ediuZDET5-Soy1IpGGJzm6d9N4hWitYLfYVMb07FN9xwYBsDsKtqdd5ujji6pl0sDJPSLm29fN89vagDU51RlhC8rgKWhLKScODUxIq;' + cookiesList[i] + ';pt_token=oss1b9v6;__jdb=122270672.3.16284882664002016987922|1.1628488266;mba_sid=16284882664066635066110123546.3;__jd_ref_cls=carnivalcity_1616135996494%7C41'
            }
            res = requests.post(url=url, headers=headers, data=data).json()
            # print(res)
            try:
                if res['code'] == 200 and res['data']['status'] == 6:
                    print(nickNameList[i]+'助力'+nickname+'：'+'助力成功')
                elif res['code'] == 200 and res['data']['status'] == 4:
                    print(nickNameList[i]+'助力'+nickname+'：'+'助力完成啦----')
                    break
                elif res['code'] == 200 and res['data']['status'] == 3:
                    print(nickNameList[i]+'助力'+nickname+'：'+'没助力机会了')
            except:
                pass
            time.sleep(1)

    pass

def use_thread(jd818_cookies,nicks, cookiesList,nickNameList):
    threads = []
    for i in range(len(jd818_cookies)):
        threads.append(
            threading.Thread(target=help, args=(jd818_cookies[i], nicks[i],cookiesList,nickNameList))
        )
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def start():
    printT("############{}##########".format(script_name))
    jd818_pins = getPinEnvs()
    get_jd_cookie = getJDCookie()
    cookiesList, pinNameList, nickNameList = get_jd_cookie.getcookies()
    jd818_cookies = []
    nicks = []
    for ckname in jd818_pins:
        try:
            ckNum = pinNameList.index(ckname)
            jd818_cookies.append(cookiesList[ckNum])
            nicks.append(nickNameList[ckNum])
        except Exception as e:
            try:
                ckNum = pinNameList.index(unquote(ckname))
                jd818_cookies.append(cookiesList[ckNum])
                nicks.append(nickNameList[ckNum])
            except:
                print(f"请检查被助力账号【{ckname}】名称是否正确？ck是否存在？提示：助力名字可填pt_pin的值、也可以填账号名。")
                continue
    if len(jd818_cookies) == 0:
        exit(4)
    use_thread(jd818_cookies,nicks, cookiesList,nickNameList)

if __name__ == '__main__':
    start()









