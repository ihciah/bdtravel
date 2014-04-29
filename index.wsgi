# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
#__author__= 'ihciah@gmail.com'
#__author__= 'BaiduID-ihciah'
#__author__= 'http://www.ihcblog.com'
import tornado.wsgi,urllib2,cookielib,urllib,json,time,sys,copy
import MySQLdb
import sae.const,random
#You may edit here
setpassword='ihciah'
starttime=9
#每天刷财富的开始时间(凌晨刷被封几率较大哦)
#mode不再需要手动设置！仅修改setpassword即可！

#----------------------------以下内容非必要请不要修改-------------------------------

VERSION=2.8
err=0
fcc=0
mark=0
mode=0
ferrinfo=''#严重错误
bdstoken=''
onetimecount=1#每次调用刷的次数
userids=[]#存储关注列表
blockflag=0
iy=0
reload(sys)
sys.setdefaultencoding('utf-8')
def strc(ihc1,ihc2,ihc3):
    istart = ihc1.find(ihc2)+ len(ihc2)
    if ihc1.find(ihc2)==-1:
        return ''
    iend = ihc1.find(ihc3, istart)
    if iend==-1:
        iend=len(ihc1)-1
    return ihc1[istart:iend]
def strcall(a,b,c):
    u=0
    r=[]
    while(1):
        u=a.find(b,u+1)
        if u==-1:
            break
        else:
            tt=a.find(c,u+len(b)+1)
            r.append(a[u+len(b):tt])
    return copy.copy(r)
def getid(page):
    global mode,userids
    u=0
    l=0
    r=[]
    if mode==0:
        ran=random.choice([0,1])
        if ran==1:
            a=urllib2.urlopen("http://lvyou.baidu.com/pictravel/ajax/getpictravels?query_type=0&pn="+str(page)).read()
            r=strcall(a,'"ptid":"','"')
            r.append('pic')
        else:
            a=urllib2.urlopen("http://lvyou.baidu.com/search/ajax/searchnotes?format=ajax&type=0&pn=%s&rn=20" %page).read()
            r=strcall(a,'"nid":"','"')
            r.append('note')
        userids=strcall(a,'"uid":"','"')
    else:
        page=random.randint(1, 1000)
        a=urllib2.urlopen("http://lvyou.baidu.com/search/ajax/searchnotes?format=ajax&type=0&pn=%s&rn=20" %page).read()
        r=strcall(a,'"nid":"','"')
        userids=strcall(a,'"uid":"','"')
        r.append('note')
    return r
def htmlr(str):
    rdict={'&quot;':'"',
           '&gt;':'>',
           '&lt;':'<',
           'nbsp;':' ',#@百度管理员:你们是不是漏掉了一个'&'符号？
           '&amp;':'&',
           '&nbsp;':' '#万一哪天改对了我代码还能用^_^
    }
    for (k,v) in  rdict.items():
        str=str.replace(k,v)
    return str
def zan(id,opener,typeflag):
    global mode, fcc,ferrinfo,mark,bdstoken,blockflag
    if mode==0:
        if typeflag=='pic':
            rr=opener.open('http://lvyou.baidu.com/pictravel/'+str(id)).read()
            bdstoken=strc(rr,'bdstoken":"', '"')
            data=urllib.urlencode({'xid': str(id),'type': '10', 'bdstoken': bdstoken})
        else:
            rr=opener.open('http://lvyou.baidu.com/notes/'+str(id)).read()
            bdstoken=strc(rr, 'bdstoken":"', '"')
            data=urllib.urlencode({'xid': str(id), 'type': '1', 'bdstoken': bdstoken})
    else:
        rr=opener.open('http://lvyou.baidu.com/notes/'+str(id)).read()
        bdstoken=strc(rr, 'bdstoken":"', '"')
        hf=strc(rr,'<div class="fl">回 复','|')
        data=urllib.urlencode({'xid': str(id), 'type': '1', 'bdstoken': bdstoken})
        if hf.isdigit():
            hf=int(hf)
            if hf>=300:#300回复(20页)以上
                if random.choice([1,0,0,0])==1:#1/4几率回复

                # @百度旅游管理员:我知道你会看到这段话,我们只是刷点宝贝,玩玩而已,不要太认真嘛~
                # 而且新版本的代码已经只能获取很少的财富值了!

                    page=random.randint(7, 20)
                    pl=opener.open('http://lvyou.baidu.com/notes/'+str(id)+'-'+str(page*15)).read()
                    pl=htmlr(pl)
                    ycpl=strcall(a,'楼</span><p>','</p>')#原创评论
                    if len(ycpl)==0:
                        ycpl=strcall(a,'</span></div></div><p></p><p>','</p>')#引用评论
                        data=urllib.urlencode({'xid': str(id), 'type': '1', 'bdstoken': bdstoken,'recommend_word':ycpl})
    res=opener.open('http://lvyou.baidu.com/user/recommend/save?format=ajax', data).read()
    if res.find('User has recommended') != -1:#本游记已赞
        return 1
    if res.find('"errno": null,')!=-1 or res.find('user has no rights')!=-1:#cookie失效或被封则将用户加入错误列表，停止刷号
        fcc+=1
        ferrinfo=res
        if res.find('user has no rights')!=-1:
            blockflag=1
    if mark==1:#添加至收藏
        time.sleep(2+random.randint(1,5))
        url='http://lvyou.baidu.com/user/favorite/save?format=ajax'
        data=urllib.urlencode({'xid': str(id),'type': '1', 'bdstoken': bdstoken})
        opener.open(url,data)
    return 0
def follow(opener):
    global bdstoken,userids
    url1='http://lvyou.baidu.com/user/follow/save?format=ajax'
    url2='http://lvyou.baidu.com/user/follow/cancel?format=ajax'
    data=urllib.urlencode({'uid': random.choice(userids), 'bdstoken': bdstoken})
    if random.choice([1,1,0])==1:
        opener.open(url1,data)#2/3几率关注
        if random.choice([1,1,1,1,0])==0:
            opener.open(url2,data)#其中1/5的几率取消关注
def moresafe(string):
    blocklist=['"',"'",'%','<','(','*',')','>','`']
    sqllist=['select','drop','union','update','infile','where']
    strlow=string.lower()
    for i in blocklist:
        string=string.replace(i,'')
    for i in sqllist:
        if strlow.find(i)!=-1:
            string='ATTACK'#危险字符探测
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
def initall():
    global fcc, mode, ferrinfo,mark,starttime,onetimecount,blockflag,bdstoken,userids
    err=0
    fcc=0
    mark=0
    mode=0
    ferrinfo=''#严重错误
    bdstoken=''
    onetimecount=1#每次调用刷的次数
    userids=[]#存储关注列表
    blockflag=0
def zanpage(pageid,cc):
    global onetimecount
    ids=getid(str(pageid))
    ua='Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36'
    opener=urllib2.build_opener()
    opener.addheaders = [('User-Agent', ua)]
    opener.addheaders = [('Cookie', cc)]
    urllib2.install_opener(opener)
    ti=0
    if random.choice([1,1,1,1,0])==0:
        follow(opener)
    while ti<int(onetimecount):
        if 'pic' in ids:
            typeflag='pic'
            ids.remove('pic')
        else:
            typeflag='note'
            ids.remove('note')
        theone=random.choice(ids)
        ids.remove(theone)
        if zan(theone,opener,typeflag)==0:
            ti=ti+1
        else:
            global err
            err=err+1
def updinfo(ver):
    try:
        urr=urllib2.urlopen("aHR0cDovL2Rldi5paGNibG9nLmNvbS9jb2RlL2JkdGpzb24uaHRtbA==".decode('base64').replace('\n','')+'?appid='+sae.const.APP_NAME+'&ver='+str(ver)).read()
        upd=strc(urr,'<ver>','</ver>')
        result='最新版本:'+str(upd)
        if float(ver)<float(upd):
            downloadurl=strc(urr,'<download>','</download>')
            changedata=strc(urr,'<logdata>','</logdata>')
            changelist=json.loads(changedata)
            changelist=sorted(changelist, key=lambda m : m['ver'])
            for i in changelist:
                i['log']=i['log'].replace("<br>",'\n')
                i['log']=i['log'].replace("<br \>",'\n')
                i['log']=i['log'].replace("<br\>",'\n')
            if downloadurl!='':
                result+='\n下载地址：%s' %downloadurl
            result+='\n在新的版本里做了如下更新:'
            for i in changelist:
                if float(i['ver'])>float(ver) and float(i['ver'])<=float(upd):
                    result=result+'\n  '+str(i['ver'])
                    result=result+':'+i['log'].encode('utf-8')
        else:
            result+='\n\n[请访问http://tieba.baidu.com/p/2972991643(贴吧链接)\nhttps://github.com/ihciah/bdtravel(Github)\n获取更新]'
    except:
        result= '\n更新服务器出BUG了，记得手动检查更新哦~'
    return result


class Shua(tornado.web.RequestHandler):
    def get(self):
        global fcc, mode, ferrinfo,mark,starttime,onetimecount,blockflag,bdstoken,userids,iy
        if starttime not in dir():
            starttime=9
        if int(time.strftime("%H"))<int(starttime):
            self.write('Time is not correct.Task will be started after %d:00.'%int(starttime))
            return
        if random.choice([1,1,0,0,1,0])==0:#1/2的几率不执行任务
            self.write('pass.maybe next time~')
            return
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
        if (info['time']==25-int(onetimecount) and mode==1) or (info['time']==20-int(onetimecount) and mode==0):
            addition=0
        else:
            addition=random.choice([0,0,1])#添加额外随机次数，不刷满
        cursor.execute("UPDATE bdaccounts SET time=%d WHERE sid='%s'" %(info['time']+int(onetimecount)+addition,info['sid']))
        self.write(str(onetimecount)+' "Zan" have been submited.<br>Number of the repeated topic:'+str(err))
        if fcc>=onetimecount and blockflag==0:
            self.write('<br>Fatal Error:Maybe this cookie is wrong or out of date')
            cursor.execute("UPDATE bdaccounts SET time=500,cookie='ERROR' WHERE sid='%s' AND cookie='%s'" %(info['sid'],info['cookie']))
            self.write('<br>This account has been disabled due to wrong cookie.')
            self.write('<br>Err info:<br>')
            self.write(ferrinfo)
        if fcc>=onetimecount and blockflag==1:
            self.write('<br>Fatal Error:This account has been blocked by baidu.')
            preference[0]['block']=1
            jp=json.dumps(preference)
            cursor.execute("UPDATE bdaccounts SET time=500,cookie='ERROR',preference='%s' WHERE sid='%s' AND cookie='%s'" %(jp,info['sid'],info['cookie']))
            self.write('<br>Err info:<br>')
            self.write(ferrinfo)
        mydb.close()
        self.write('<br><br><a href="/">Return homepage</a><br>')
        while iy<3:#刷的太慢了..加速一下...懒得重写函数什么的了,这么凑或用吧
            initall()
            iy+=1
            time.sleep(3)
            self.get()
class Set(tornado.web.RequestHandler):
    def post(self):
        cookie=str(self.get_argument('cookie',''))
        sid=str(self.get_argument('sid',''))
        psw=str(self.get_argument('psw',''))
        mark=int(self.get_argument('mark','0'))
        mode=int(self.get_argument('mode','0'))
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
        self.render("html/set.html")

class Reset(tornado.web.RequestHandler):
    def get(self):
        mydb = getmydb()
        cursor = mydb.cursor()
        cursor.execute("UPDATE bdaccounts SET time=0 WHERE cookie!='ERROR'")
        self.write('Counter has been reset. :)')
        mydb.close()
        self.write('<br><br><a href="/">Return homepage</a>')
class About(tornado.web.RequestHandler):
    def get(self):
        self.render("html/about.html")
class Home(tornado.web.RequestHandler):
    def get(self):
        global err,fcc,mode,VERSION,starttime
        mydb = getmydb()
        cursor = mydb.cursor()
        jcount=int(cursor.execute("select * from bdaccounts where time<100 and cookie!='ERROR'"))
        jstr=''
        rcount=0
        allcount=0
        errlist=[]
        blocklist=[]
        finlist=[]
        for row in cursor.fetchall():
            rcount+=int(row[2])
            if row[4]==1:
                allcount+=25
            else:
                allcount+=20
        jstr=str(rcount)+'/'+str(allcount)
        ppp=str(cursor.execute("SELECT * FROM bdaccounts WHERE (time>=25 AND time<500 AND mode=1) OR (time=20 AND time<500 AND mode=0)"))#所有完成的正确账号
        pp=str(cursor.execute("SELECT * FROM bdaccounts"))#所有账号数，包括已完成，未完成，错误号
        p=str(cursor.execute("select * from bdaccounts where cookie='ERROR'"))#错误账号
        ppp=str(ppp)
        for row in cursor.fetchall():
            #errlist.append(row[0][:4]+'*'*(len(row[0])-4))
            errlist.append(row[0])
        bc=cursor.execute("select * from bdaccounts where cookie='ERROR' and preference REGEXP  '\"block\": 1'")#被封账号
        for row in cursor.fetchall():
            blocklist.append(row[0])
        for i in errlist:
            if i in blocklist:
                finlist.append(i[:4]+'*'*(len(i)-4)+' -百度已封号')
            else:
                finlist.append(i[:4]+'*'*(len(i)-4))
        if p=='0':
            finlist.append('恭喜~没有Cookie出错的用户哦 :)')
        self.render("html/index.html",p=p,pp=pp,ppp=ppp,jstr=jstr,errlist=finlist,VERS=str(VERSION),newv=updinfo(VERSION),starttime=str(starttime),blockcount=int(bc))
        mydb.close()

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
        if 'mydb' not in dir():
            self.write('Mysql server has not been opened.Please open it in SAE adminpage')
            return
        mydb.close()
        self.write('Database has benn initialized. :)<br>This function is of no use from now on.')
app = tornado.wsgi.WSGIApplication([
  ('/shua', Shua),
  ('/set', Set),
  ('/reset',Reset),
  ('/',Home),
  ('/init',Initialize),
  ('/about',About),

], debug=True)


application = sae.create_wsgi_app(app)