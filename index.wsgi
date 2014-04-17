# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
#__author__= 'ihciah@gmail.com'
#__author__= 'BaiduID-ihciah'
#__author__= 'http://www.ihcblog.com'
import tornado.wsgi,urllib2,cookielib,urllib,json,time
import MySQLdb
import sae.const,random
#You may edit here
setpassword='ihciah'

#mode不再需要手动设置！仅修改setpassword即可！

#------------------------------------------------------------------------

VERSION=2.7
err=0
fcc=0
mark=0
mode=1
ferrinfo=''
def strc(ihc1,ihc2,ihc3):
    istart = ihc1.find(ihc2)+ len(ihc2)
    if ihc1.find(ihc2)==-1:
        return ''
    iend = ihc1.find(ihc3, istart)
    if iend==-1:
        iend=len(ihc1)-1
    return ihc1[istart:iend]
def getid(page):
    global mode
    u=0
    r=[]
    if mode==0:
        a=urllib2.urlopen("http://lvyou.baidu.com/pictravel/ajax/getpictravels?query_type=0&pn="+str(page)).read()
        while(1):
            u=a.find('"ptid":"',u+1)
            if u==-1:
                break
            else:
                tt=a.find('"',u+len('"ptid":"')+1)
                r.append(a[u+len('"ptid":"'):tt])
    else:
        page=random.randint(1, 1000)
        a=urllib2.urlopen("http://lvyou.baidu.com/search/ajax/searchnotes?format=ajax&type=0&pn=%s&rn=20" %page).read()
        while(1):
            u=a.find('"nid":"',u+1)
            if u==-1:
                break
            else:
                tt=a.find('"',u+len('"nid":"')+1)
                r.append(a[u+len('"nid":"'):tt])
    return r

def zan(id,opener):
    global mode, fcc,ferrinfo,mark
    if mode==0:
        rr=opener.open('http://lvyou.baidu.com/pictravel/'+str(id)).read()
        bdstoken=strc(rr,'bdstoken":"', '"')
        data=urllib.urlencode({'xid': str(id),'type': '10', 'bdstoken': bdstoken})
    else:
        rr=opener.open('http://lvyou.baidu.com/notes/'+str(id)).read()
        bdstoken=strc(rr, 'bdstoken":"', '"')
        data=urllib.urlencode({'xid': str(id), 'type': '1', 'bdstoken': bdstoken, 'recommend_word': ''})
    res=opener.open('http://lvyou.baidu.com/user/recommend/save?format=ajax', data).read()
    if res.find('User has recommended') != -1:
        return 1
    if res.find('"errno": null,')!=-1:
        fcc+=1
        ferrinfo=res
    if mark==1:
        url='http://lvyou.baidu.com/user/favorite/save?format=ajax'
        data=urllib.urlencode({'xid': str(id),'type': '1', 'bdstoken': bdstoken})
        opener.open(url,data)
    return 0
def moresafe(string):
    blocklist=['"',"'",'%','<','(','*',')','>','`']
    sqllist=['select','drop','union','update','infile','where']
    strlow=string.lower()
    for i in blocklist:
        string=string.replace(i,'')
    for i in sqllist:
        if strlow.find(i)!=-1:
            string='ATTACK'
    return string

def getmydb():
    mydb = MySQLdb.connect(
        host   = sae.const.MYSQL_HOST,
        port   = int(sae.const.MYSQL_PORT),
        user   = sae.const.MYSQL_USER,
        passwd = sae.const.MYSQL_PASS,
        db = sae.const.MYSQL_DB,
        charset = 'utf8')
    return mydb

def zanpage(pageid,cc):
    ids=getid(str(pageid))
    ua='Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36'
    #cookie=cookielib.CookieJar()
    #opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    opener=urllib2.build_opener()
    opener.addheaders = [('User-Agent', ua)]
    opener.addheaders = [('Cookie', cc)]
    urllib2.install_opener(opener)
    ti=0
    while ti<5:
        theone=random.choice(ids)
        ids.remove(theone)
        if zan(theone,opener)==0:
            ti=ti+1
        else:
            global err
            err=err+1
def updinfo(ver):
    try:
        global mode
        urr=urllib2.urlopen("aHR0cDovL2Rldi5paGNibG9nLmNvbS9jb2RlL2JkdGpzb24uaHRtbA==".decode('base64').replace('\n','')+'?appid='+sae.const.APP_NAME+'&mode='+str(mode)+'&ver='+str(ver)).read()
        upd=strc(urr,'<ver>','</ver>')
        result='<br>最新版本:'+str(upd)
        if float(ver)<float(upd):
            downloadurl=strc(urr,'<download>','</download>')
            changedata=strc(urr,'<logdata>','</logdata>')
            changelist=json.loads(changedata)
            changelist=sorted(changelist, key=lambda m : m['ver'])
            result+='<br><br>在新的版本里做了如下更新:'
            for i in changelist:
                if float(i['ver'])>float(ver):
                    result=result+'<br>&nbsp;&nbsp;V'+str(i['ver'])
                    result=result+':'+i['log'].encode('utf-8')
            if downloadurl!='':
                result+='<br><br><a href="%s">>>请点击这里下载并更新源代码<<</a>' %downloadurl
            else:
                result+='<br><br>[请访问<a href="http://tieba.baidu.com/p/2972991643">贴吧链接</a>获取更新]|[<a href="https://github.com/ihciah/bdtravel">Github</a>]'
    except:
        result= '<br>更新服务器出BUG了，记得手动检查更新哦~'
    return result


class Shua(tornado.web.RequestHandler):
    def get(self):
        global fcc, mode, ferrinfo,mark
        fcc=0
        page=random.randint(1, 800)
        mydb = getmydb()
        cursor = mydb.cursor()
        ppp=cursor.execute('SELECT * FROM bdaccounts WHERE (time<20 AND mode=0) OR (time<25 AND mode=1) ORDER BY RAND() LIMIT 1')
        if int(ppp)==0:
            self.write("There's no task today,all tasks have been finished :)<br>Wanna check code update?<a href=\"http://tieba.baidu.com/p/2972991643\">Baidu post</a> | <a href=\"https://github.com/ihciah/bdtravel\">Github</a>")
            mydb.close()
            self.write('<br><br><a href="/">Return homepage</a>')
            return
        result=cursor.fetchone()
        info={}
        info['sid']=result[0]
        info['cookie']=result[1]
        info['time']=int(result[2])
        mode=int(result[4])
        info['pre']=str(result[3])
        preference=json.loads(info['pre'])
        if len(preference)!=0 and preference[0]['mark'] is not None and preference[0]['mark']==1:
            mark=1
        else:
            mark=0
        zanpage(page,info['cookie'])
        cursor.execute("update bdaccounts set time=%d where sid='%s'" %(info['time']+5,info['sid']))
        
        self.write('5 "Zan" have been submited.<br>Number of the repeated topic:'+str(err))
        if fcc>=5:
            self.write('<br>Fatal Error:Maybe this cookie is wrong or out of date')
            cursor.execute("update bdaccounts set time=500,cookie='ERROR' where sid='%s' and cookie='%s'" %(info['sid'],info['cookie']))
            self.write('<br>This account has been disabled due to wrong cookie.')
            self.write('<br>Err info:<br>')
            self.write(ferrinfo)
        mydb.close()
        self.write('<br><br><a href="/">Return homepage</a>')
class Set(tornado.web.RequestHandler):
    def post(self):
        cookie=str(self.get_argument('cookie',''))
        sid=str(self.get_argument('sid',''))
        psw=str(self.get_argument('psw',''))
        mark=int(self.get_argument('mark','0'))
        mode=int(self.get_argument('mode','1'))
        cookie=moresafe(cookie)
        sid=moresafe(sid)[:200]
        if mark!=1 and mark!=0:
            mark=0
        if mode!=1 and mode!=0:
            mode=0
        jpre=json.dumps([{'mark':mark}])
        if cookie=='ATTACK' or sid=='ATTACK':
            self.write("ATTACK DETECTED.DON'T USE SQL KEYWORDS(SUCH AS select,drop,where) IN FORM DATA.")
            return
        if psw!=setpassword:
            self.write("Your password is not correct.Please contact webmaster for more information.<br>If u are the owner,maybe it is 'ihciah',which is the default password.<br>\
                       However,I recommend u change it(index.wsgi->Line 11).")
            self.write('<br><br><a href="/set">Return setting page.</a>')
            return
        if sid=='' or cookie=='':
            self.write("SID and COOKIE can not be blank.")
            self.write('<br><br><a href="/set">Return setting page.</a>')
            return
        mydb = getmydb()
        cursor = mydb.cursor()
        rt=int(cursor.execute("update bdaccounts set cookie='%s',time=0,preference='%s',mode=%d where sid='%s'" %(cookie,jpre,mode,sid)))
        if rt==0:
            cursor.execute("insert into bdaccounts values('%s','%s',0,'%s',%d)" %(sid,cookie,jpre,mode))
            self.write("New user has been added :)<br>New user's sid:"+sid)
            if mode==1:
                self.write(" | mode:Greedy mode | ")
            else:
                self.write(" | mode:Safe mode | ")
            if mark==1:
                self.write("Add bookmark auto")
        else:
            self.write('User cookie and preference have been updated successfully.')
        mydb.close()
        self.write('<br><br><a href="/">Return homepage</a>')
    def get(self):
        self.write('''
        <html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
          <title>Set BDCOOKIE</title></head>
          <body>
          <h1 style="text-align:center">添加用户 & 更新Cookie</h1>
          <form style="text-align:center" action="/set" method="post" accept-charset="utf-8">
            <div>sid:<textarea name="sid" value="" rows="1" cols="50"></textarea></div>
            <div>cookie:</div><div><textarea name="cookie" value="" rows="5"></textarea></div>
            <div>Mode:<select name="mode"><option value=1 selected>贪婪模式</option><option value=0>安全模式</option></select></div>
            <div>Add bookmark:<select name="mark"><option value=0 selected>不添加</option><option value=1>添加</option></select></div>
            <div>Password:<input name="psw" type="password" size=10 /></div>
            <div><input type="submit" value="Submit"></div>
          </form>
          <br><p style="text-align:center"><a href="/"><-Return homepage</a></p><br><br>
          <p style="text-align:center">Note:</p>
          <p style="text-align:center"><font color="red">【SID】</font></p>
          <p style="text-align:center">SID不一定是百度ID，可以是英文和数字的任意组合。</p>
          <p style="text-align:center">初始设定时SID随意取，但更新cookie时需要输入初始设定的sid，所以请记住(忘记请登录SAE点击数据库管理去看)</p>
          <p style="text-align:center">每个SID唯一对应一个账号，为防止他人改动你的cookie，请设置4位以上，首页将在cookie过期时显示sid前4位</p>
          <p style="text-align:center"><font color="red">【如何获取COOKIE】(javascript方式可能出错)</font></p>
          <p style="text-align:center"></p>
          <p style="text-align:center">1.使用chrome新打开一个隐身标签页（注意是隐身标签页）</p>
<p style="text-align:center">2.打开lvyou.baidu.com并登陆</p>
<p style="text-align:center">3.点击F12</p>
<p style="text-align:center">4.刷新该页面</p>
<p style="text-align:center">5.在下方的开发者工具中选择Network标签，拉到最上边，点击第一个包(名为lvyou.baidu.com)，右侧点击Header标签</p>
<p style="text-align:center">6.把Request Header中的Cookie复制下来（直接复制，所有的都复制下来扔进去）</p>


<p style="text-align:center">Cookie格式像这样(其实只需要有关键的几项就够了)：</p>

HMACCOUNT=EE7823421DWCE1; BAIDUID=893165EDQWFWQF213215905F223424:FG=1; BAIDU_WISE_UID=wapp_13941231390_446; Hm_lvt_f4165dfug3i4g2ifse6few70a6bd243=1393233964,1396627467; BDUSS=NCV2pkZjZCeGZnN2VmNWc2Z1N6VHBJN25MNXBTQllsTDBuRy0tVDWQFWfewfwFEWFWEBJCQAAAAAAAADWQEFW#44w5gtaWhjaWFoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANREWFEWFEWW; MCITY=-%3A; cflag=65535%3A1


<p style="text-align:center">至此Cookie已提取成功。直接关闭浏览器（别点退出，否则cookie失效）</p>

<p style="text-align:center">本方法对新手可能较为复杂，可自行百度其他获取cookie的方法</p>
<p style="text-align:center">（各大云签到都有教哦，但要注意格式，这个使用的cookie是带着键名的）</p>
<p style="text-align:center"><font color="red">【PASSWORD】</font></p>
<p style="text-align:center">密码为index.wsgi中11行设置的密码。默认为ihciah，最好修改掉。</p>
<p style="text-align:center">只有拥有这个密码才可以使用本系统。</p>
<p style="text-align:center"><font color="red">【模式和收藏】</font></p>
<p style="text-align:center">贪婪模式每天+1750财富，安全模式每天+500财富.贪婪模式下被百度封号几率较大.</p>
<p style="text-align:center">收藏功能开启时会自动收藏游记，每天额外+500财富，但会影响收藏功能使用.</p>
          </body>
          </html>''')

class Reset(tornado.web.RequestHandler):
    def get(self):
        mydb = getmydb()
        cursor = mydb.cursor()
        cursor.execute("update bdaccounts set time=0 where cookie!='ERROR'")
        self.write('Counter has been reset. :)')
        mydb.close()
        self.write('<br><br><a href="/">Return homepage</a>')

class Home(tornado.web.RequestHandler):
    def get(self):
        global err,fcc,mode,VERSION
        mydb = getmydb()
        cursor = mydb.cursor()
        jcount=int(cursor.execute("select * from bdaccounts where time<100 and cookie!='ERROR'"))
        jstr=''
        rcount=0
        allcount=0
        for row in cursor.fetchall():
            rcount+=int(row[2])
            if row[4]==1:
                allcount+=25
            else:
                allcount+=20
        jstr=str(rcount)+'/'+str(allcount)
        if rcount==0 and int(time.strftime("%H"))>1:
            jstr+=' - <font color="red">请检查你的config.yaml配置!</font>'
        ppp=str(cursor.execute("SELECT * FROM bdaccounts WHERE (time>=25 AND time<500 AND mode=1) OR (time=20 AND time<500 AND mode=0)"))#所有完成的正确账号
        pp=str(cursor.execute("SELECT * FROM bdaccounts"))#所有账号数，包括已完成，未完成，错误号
        p=str(cursor.execute("select * from bdaccounts where cookie='ERROR'"))#错误账号
        ppp=str(ppp)
        self.write('<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/><title>Coin fetcher for Baidu Travel</title>')
        self.write('<script type="text/javascript">function show_confirm(){var r=confirm("此操作将导致所有计数器归零，所有刷分操作重新开始。确认？");if (r==true){location.href ="/reset";}}function shua(){location.href ="/shua";}</script></head><body>')
        self.write('<h1>Simple BaiDu Travel coin fetcher</h1><br><br><br>现有账号数:'+pp+'<br>今日已完成:'+ppp+'账号<br>总进度:'+jstr+'<br>Cookie错误账号数:'+p+'<br>错误Cookie的SID列表:')
        for row in cursor.fetchall():
            self.write('<br>&nbsp;&nbsp;&nbsp;&nbsp;'+row[0][:4]+'*'*(len(row[0])-4))
        if p=='0':
            self.write('<br>&nbsp;&nbsp;&nbsp;&nbsp;恭喜~没有Cookie出错的用户哦 :)')
        self.write('<br><br><a href="/set">>>>更新Cookie或登记新账号，请点这里<<<</a><br><br>调试工具(仅供管理员调试之用):<br><input type="button" onclick="shua()" value="手动调用" /><br><input type="button" onclick="show_confirm()" value="重置所有计数器" /><br>\
        <br>Source Code:</br><a href="https://github.com/ihciah/bdtravel" target="_blank">Github</a> | <a href="http://tieba.baidu.com/p/2972991643" target="_blank">Tieba post</a><br>By ihciah(www.ihcblog.com)')
        self.write('<br><br>你的应用版本:'+str(VERSION))
        self.write(updinfo(VERSION))
        mydb.close()
        self.write('</body></html><!--HTML代码纯手敲，是有点简陋-_-||-->')
class Initialize(tornado.web.RequestHandler):
    def get(self):
        try:
            mydb = getmydb()
            cursor = mydb.cursor()
            cmd='''CREATE TABLE IF NOT EXISTS `bdaccounts` (
  `sid` char(200) NOT NULL,
  `cookie` longtext NOT NULL,
  `time` int(11) NOT NULL,
  PRIMARY KEY (`sid`),
  UNIQUE KEY `sid` (`sid`));'''
            cursor.execute(cmd)
            cmd="ALTER IGNORE TABLE bdaccounts ADD preference char(255) NOT NULL default '[]';"
            cursor.execute(cmd)
        except:
            pass
        try:
            cmd="ALTER IGNORE TABLE bdaccounts ADD mode int(5) NOT NULL default 1;"
            cursor.execute(cmd)
        except:
            pass
        mydb.close()
        self.write('Database has benn initialized. :)<br>This function is of no use from now on.')


app = tornado.wsgi.WSGIApplication([
  ('/shua', Shua),
  ('/set', Set),
  ('/reset',Reset),
  ('/',Home),
  ('/init',Initialize),

], debug=True)


application = sae.create_wsgi_app(app)