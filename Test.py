#!/usr/bin/python
# -*- coding: utf-8 -*- 
import urllib,urllib2,json,base64,md5,time
from multiprocessing import Pool
import requests

Base_URL        = "http://127.0.0.1:8888/"
DownLoad_URL    = Base_URL+"download/"
DownLoad_API_URL= Base_URL+"api/download/"
Upload_URL      = Base_URL+"upload/"
Upload_API_URL  = Base_URL+"api/upload/"
Delete_URL      = Base_URL+"delete/"
Delete_API_URL  = Base_URL+"api/delete/"
List_URL        = Base_URL+"list/"
List_API_URL    = Base_URL+"api/list/"
MD5_URL         = Base_URL+"md5/"
MD5_API_URL     = Base_URL+"api/md5/"
Info_URL        = Base_URL+"info/"
Info_API_URL    = Base_URL+"api/info/"


def test(c):
    mfile='Test.py'
    fr=open(mfile,"rb").read()
    filecontent=base64.b64encode(fr)
    filemd5=md5.new(fr).hexdigest()
    files = {'file': open(mfile,"rb")}
    r = requests.post(Upload_URL,files=files,data={'path':'/upload'})
    print r.text   

    r = requests.post(List_URL,{"path":"/upload"})
    print r.text

    r = requests.post(MD5_URL,{"filename":"/upload/"+mfile})
    print r.text

    r = requests.post(Info_URL,{"filename":"/upload/"+mfile})
    print r.text

    r = requests.get(DownLoad_URL+"upload/"+mfile)
    print len(r.text)

    r = requests.post(Delete_URL,{"filename":"/upload/"+mfile})
    print r.text

def testapi(c):
    filename='Test.py'
    fr=open(filename,"rb").read()
    filecontent=base64.b64encode(fr)
    filemd5=md5.new(fr).hexdigest()
    filename='Test_%s.py'%c
  #  print filename, filemd5

    opener=urllib2.urlopen(List_API_URL,json.dumps({"path":"/upload"}))
    obj = json.loads(opener.read())
  #  print obj['success'],obj['message']

    opener=urllib2.urlopen(List_API_URL,json.dumps({"path":"/upload1"}))
    obj = json.loads(opener.read())
  #  print obj['success'],obj['message']

    opener=urllib2.urlopen(MD5_API_URL,json.dumps({"filename":"/upload/"+filename}))
    obj = json.loads(opener.read())
  #  print obj['success'],obj['message']

    opener=urllib2.urlopen(MD5_API_URL,json.dumps({"filename":"/upload1/"+filename}))
    obj = json.loads(opener.read())
  #  print obj['success'],obj['message']

    opener=urllib2.urlopen(Upload_API_URL,json.dumps({"filename":filename,"path":"/upload","content":filecontent,"md5":filemd5}))
    obj = json.loads(opener.read())
#    print obj['success'],obj['message']

    opener=urllib2.urlopen(Upload_API_URL,json.dumps({"filename":filename,"path":"/upload","content":filecontent,"md5":"xxxxxx"}))
    obj = json.loads(opener.read())
#    print obj['success'],obj['message']

    opener=urllib2.urlopen(DownLoad_API_URL,json.dumps({"filename":"/upload/"+filename,}))
    obj = json.loads(opener.read())
#    print obj['success'],obj['message']

    opener=urllib2.urlopen(DownLoad_API_URL,json.dumps({"filename":"/upload1/"+filename,}))
    obj = json.loads(opener.read())
#    print obj['success'],obj['message']

    opener=urllib2.urlopen(Info_API_URL,json.dumps({"filename":"/upload/"+filename,}))
    obj = json.loads(opener.read())
#    print obj['success'],obj['message']

    opener=urllib2.urlopen(Info_API_URL,json.dumps({"filename":"/upload1/"+filename,}))
    obj = json.loads(opener.read())
#    print obj['success'],obj['message']

    opener=urllib2.urlopen(Delete_API_URL,json.dumps({"filename":"/upload/"+filename,}))
    obj = json.loads(opener.read())
#    print obj['success'],obj['message']

    opener=urllib2.urlopen(Delete_API_URL,json.dumps({"filename":"/upload1/"+filename,}))
    obj = json.loads(opener.read())
#    print obj['success'],obj['message']

    print c, "end" 

if __name__ == '__main__':
    #普通网页调用测试
    test(0)
    #API调用测试
    start=time.clock()
    pool = Pool(processes=20)
    pool.map(testapi, xrange(1000)) 
    pool.close()
    pool.join()
    print "time used:", time.clock()-start

