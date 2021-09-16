#!/bin/env python3
# -*- coding: utf-8 -*
#京喜88领红包A版
#cron 5 0,20 0 * * *

# export jx88_pins=["pt_pin1","pt_pin2"]

from urllib.parse import unquote, quote
import time, datetime, os, sys
import requests, json, re, random
import threading

UserAgent = ''
script_name = '京喜88领红包A版'
BASE_URL = 'https://wq.jd.com/cubeactive/steprewardv3'
activeId = '489177'
UA = 'jdpingou;iPhone;4.13.0;14.4.2;network/wifi;model/iPhone10,2;appBuild/100609;ADID/00000000-0000-0000-0000-000000000000;supportApplePay/1;hasUPPay/0;pushNoticeIsOpen/1;hasOCPay/0;supportBestPay/0;session/${Math.random * 98 + 1};pap/JA2019_3111789;brand/apple;supportJDSHWK/1;Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'


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
                    cookiesList.append(ck)
                    pinNameList.append(pinName)
                    user_order += 1

                    # 获取账号名
                    # ck, nickname = self.getUserInfo(ck, user_order, pinName)
                    # if nickname != False:
                    #     cookiesList.append(ck)
                    #     pinNameList.append(pinName)
                    #     nickNameList.append(nickname)
                    #     user_order += 1
                    # else:
                    #     user_order += 1
                    #     continue

                if len(cookiesList) > 0:
                    return cookiesList, pinNameList, nickNameList
                else:
                    printT("没有可用Cookie，已退出")
                    exit(4)
        else:
            printT("没有可用Cookie，已退出")
            exit(4)


def getPinEnvs():
    if "jx88_pins" in os.environ:
        if len(os.environ["jx88_pins"]) != 0:
            jx88_pins = os.environ["jx88_pins"]
            jx88_pins = jx88_pins.replace('[', '').replace(']', '').replace('\'', '').replace(' ', '').split(',')
            printT(f"已获取并使用Env环境 jx88_pins:{jx88_pins}")
            return jx88_pins
        else:
            printT('请先配置export jx88_pins=["pt_pin1","pt_pin2"]')
            exit(4)
    printT('请先配置export jx88_pins=["pt_pin1","pt_pin2"]')
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


def taskurl(cookie, function_path, stk, body=''):
    url = f'{BASE_URL}/{function_path}?activeId={activeId}&publishFlag=1&channel=7&{body}&sceneval=2&g_login_type=1&timestamp={int(time.time())}&_={int(time.time()) + 2}&_ste=1&_stk={stk}'
    headers = {
        'Host': 'm.jingxi.com',
        'Cookie': cookie,
        'Accept': "*/*",
        'Accept-Encoding': 'gzip, deflate, br',
        'User-Agent': UA,
        'Accept-Language': 'zh-cn',
        'Referer': f'https://act.jingxi.com/cube/front/activePublish/step_reward/{activeId}.html'
    }
    try:
        res = requests.get(url=url, headers=headers).json()
        return res
    except:
        return -1


# 参与活动
def joinActive(mycookie):
    function_path = 'JoinActive'
    stk = 'activeId,channel,phoneid,publishFlag,stepreward_jstoken,timestamp'
    body = ''
    res = taskurl(mycookie, function_path, stk, body)
    # print(res)
    if res != -1:
        if res['iRet'] == 0:
            print(f"活动开启成功,助力邀请码为：{res['Data']['strUserPin']}")
            return res['Data']['strUserPin'],0
        elif res['iRet'] == 2012 and '用户己参与活动' in res['sErrMsg']:
            strUserPin, dwGrade = getUserInfo(mycookie)
            if strUserPin == 0:
                print(f'{dwGrade}个阶梯红包已全部获得')
                return 0, dwGrade
            elif strUserPin == -1:
                print('获取助力码失败')
                return -1, 0
            else:
                if dwGrade != 0:
                    print(f"已获得第{dwGrade}个阶梯红包，获取助力码成功：{strUserPin}")
                else:
                    print(f"还没有获得红包，获取助力码成功：{strUserPin}")
                return strUserPin, dwGrade

        else:
            print(f"活动开启失败：{res['sErrMsg']}")
            return -1, 0
    else:
        print('京喜88活动开启失败')
        return -1, 0


# 获取助力码
def getUserInfo(mycookie):
    dwGrade = 0
    function_path = 'GetUserInfo'
    stk = 'aactiveId,channel,joinDate,phoneid,publishFlag,timestamp'
    body = f"joinDate={datetime.date.today().strftime('%Y%m%d')}"
    res = taskurl(mycookie, function_path, stk, body)
    if res != -1:
        if res['iRet'] == 0:
            gradeConfig = res['Data']['gradeConfig']
            dwHelpedTimes = res['Data']['dwHelpedTimes']
            for grade in gradeConfig:
                if dwHelpedTimes >= grade['dwHelpTimes']:
                    dwGrade = grade['dwGrade']
            if dwGrade != 7:
                # print(f"已获得第{dwGrade}个阶梯红包，获取助力码成功：{res['Data']['strUserPin']}")
                return res['Data']['strUserPin'], dwGrade
            else:
                # print(f'{dwGrade}个阶梯红包已全部获得')
                return 0, dwGrade
        else:
            # print(f"获取助力码失败：{res['sErrMsg']}")
            return -1, dwGrade
    else:
        # print('获取助力码失败')
        return -1, dwGrade

#开红包
def openRedPack(mycookie,strPin,j):
    function_path = 'DoGradeDraw'
    stk = 'activeId,channel,grade,phoneid,publishFlag,stepreward_jstoken,strPin,timestamp'
    for grade in range(7):
        grade = grade + 1
        body = f"strPin={strPin}&grade={grade}"
        res = taskurl(mycookie, function_path, stk, body)
        print(res)
        if res != -1:
            if res['iRet'] == 0:
                print(f"账号{j}拆第{grade}阶梯红包成功：{res['sErrMsg']}")
            elif res['iRet'] == 2018:
                print(f"账号{j}拆第{grade}阶梯红包失败：{res['sErrMsg']}")
            elif res['iRet'] == 2017:  #助力不够
                print(f"账号{j}拆第{grade}阶梯红包失败：{res['sErrMsg']}")
                break
            else:
                print(f"拆第{grade}阶梯红包失败：{res['sErrMsg']}")
        time.sleep(15)


# 助力好友
def help(mycookie,cookiesList,j):
    strPin, dwGrade = joinActive(mycookie)
    if strPin == 0:
        openRedPack(mycookie, strPin,j)
    elif strPin != 0 and strPin != -1:
        function_path = 'EnrollFriend'
        stk = 'activeId,channel,joinDate,phoneid,publishFlag,strPin,timestamp'
        body = f"strPin={strPin}&joinDate={datetime.date.today().strftime('%Y%m%d')}"
        for i in range(len(cookiesList)):
            res = taskurl(cookiesList[i], function_path, stk, body)
            # print(res)
            if res != -1:
                i = i + 1
                if res['iRet'] == 0:
                    print(f"ck{i}助力账号{j}成功🎉:{res['sErrMsg']}")
                elif res['iRet'] == 2013:
                    print(f'恭喜账号{j}已拆得所有阶梯红包了：' + res['sErrMsg'])
                    break
                elif res['iRet'] == 2000:
                    print(f'ck{i}助力账号{j}失败：' + res['sErrMsg'])  # 未登录
                elif res['iRet'] == 2015:
                    print(f'ck{i}助力账号{j}失败：' + res['sErrMsg'])  # 助力已达上限
                elif res['iRet'] == 2016:
                    print(f'ck{i}助力账号{j}失败：' + res['sErrMsg'])  # 助力火爆
                else:
                    print(f'ck{i}助力账号{j}失败：' + res['sErrMsg'])
            else:
                continue
        openRedPack(mycookie, strPin,j)


def use_thread(jx88_cookies, cookiesList):
    threads = []
    for i in range(len(jx88_cookies)):
        threads.append(
            threading.Thread(target=help, args=(jx88_cookies[i],cookiesList,i+1))
        )
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def start():
    printT("############{}##########".format(script_name))
    jx88_pins = getPinEnvs()
    get_jd_cookie = getJDCookie()
    cookiesList, pinNameList, nickNameList = get_jd_cookie.getcookies()
    jx88_cookies = []
    nicks = []
    for ckname in jx88_pins:
        try:
            ckNum = pinNameList.index(ckname)
            jx88_cookies.append(cookiesList[ckNum])
            # nicks.append(nickNameList[ckNum])
        except Exception as e:
            try:
                ckNum = pinNameList.index(unquote(ckname))
                jx88_cookies.append(cookiesList[ckNum])
                # nicks.append(nickNameList[ckNum])
            except:
                print(f"请检查被助力账号【{ckname}】名称是否正确？ck是否存在？提示：助力名字可填pt_pin的值、也可以填账号名。")
                continue
    if len(jx88_cookies) == 0:
        exit(4)
    use_thread(jx88_cookies,cookiesList)

if __name__ == '__main__':
    start()









