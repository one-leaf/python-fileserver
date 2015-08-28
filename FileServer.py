#!/usr/bin/python
# -*- coding: utf-8 -*- 

#独立的文件服务器，采用tornado框架
#wp 2015-08-27

import tornado.ioloop
import tornado.web
import os,re,md5,base64,tempfile,shutil
import json
from  tornado.escape import json_decode
from  tornado.escape import json_encode

FileStoragePath="/root/files/"

def checkAcess(fileName):
    realpath=os.path.realpath(fileName)
    if not realpath.startswith(FileStoragePath):
        print realpath,fileName
        raise tornado.web.HTTPError(403, u"你没有访问 %s 的权限"%fileName)

def ajaxCheckAcess(self,fileName):
    realpath=os.path.realpath(fileName)
    if not realpath.startswith(FileStoragePath):
        self.finish(json.dumps({"success":0,"message":u"你没有访问 %s 的权限"%fileName}))
        print realpath,fileName
        return False
    return True    

def saveToFile(saveFile,content):
    try:
        tfn=tempfile.mktemp()
        tf=open(tfn,'w+b')
        tf.write(content)
        tf.close()
        os.rename(tfn,saveFile)
        return True
    except:
        return False        

def getFileInfo(infofile):
    info={}
    info["isfile"]=os.path.isfile(infofile) 
    info["isdir"]=os.path.isdir(infofile)
    info["size"]=os.path.getsize(infofile)
    info["atime"]=os.path.getatime(infofile)
    info["mtime"]=os.path.getmtime(infofile)
    info["ctime"]=os.path.getctime(infofile)
    info["name"]=os.path.basename(infofile) 
    return info 

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(u"正常运行中.")

#API 下载文件 
#参数 {"filename":"/xxx/xxx.png"}
#filename 需要下载的文件名
class APIDownloadHandler(tornado.web.RequestHandler):
    def post(self):
        obj = json_decode(self.request.body)  
        if not obj['filename']:
            self.finish(json.dumps({"success":0,"message":u"需要下载的文件名为空"}))
            return  
        filename=obj['filename']    
        if filename.startswith('/'): filename='.'+filename                
        readFile = os.path.join(FileStoragePath,filename)
        if not ajaxCheckAcess(self,readFile): return
        if not os.path.exists(readFile):
            self.finish(json.dumps({"success":0,"message":u"需要下载的文件不存在"}))
            return
        try:            
            fs=open(readFile).read()
            fr=base64.b64encode(fs)
            md5code=md5.new(fr).hexdigest()
            self.finish(json.dumps({"success":1,"message":fr,"md5":md5code,"filename":os.path.basename(readFile)}))
        except:
            self.finish(json.dumps({"success":0,"message":u"文件下载失败"})) 


#上传文件 ，参数 files 需要上传的文件, path 保存的路径
class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        uploadfile = self.request.files['file'][0]
        path = self.get_argument('path') 
        if path ==None or path=="":
            raise tornado.web.HTTPError(500, u"你必需指定一个保存目录")
        if path.startswith('/'): path='.'+path    
        fname = uploadfile['filename']
        savePath = os.path.join(FileStoragePath,path)
        saveFile = os.path.join(savePath,fname)
        checkAcess(saveFile) 
        if os.path.exists(saveFile):
            raise tornado.web.HTTPError(500, u"文件在目录中已经存在")
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        if saveToFile(saveFile,uploadfile['body']):
            self.finish(u"文件上传成功")
        else:
            raise tornado.web.HTTPError(500, u"上传文件失败.")     

#API 上传文件
#参数 {"filename":"xxx.jpg","path":"/upload/","content":"xxxxxxx","md5":“xxxxxxxxxxxxxx”}
#     filename 保存的文件名，不带路径
#     path 保存的路径
#     content 文件的内容，采用base64编码
#     md5 文件的MD5校验值
class APIUploadHandler(tornado.web.RequestHandler):
    def post(self):
        obj = json_decode(self.request.body)
        if not obj['filename'] or not obj['path'] or not obj['content'] or not obj['md5']:
            self.finish(json.dumps({"success":0,"message":u"提交的栏位不完整，请检查"}))
            return
        path=obj['path']
        if path.startswith('/'): path='.'+path    
        savePath = os.path.join(FileStoragePath,path)
        saveFile = os.path.join(savePath,obj['filename'])
        if not ajaxCheckAcess(self,saveFile): return
        if os.path.exists(saveFile):
            self.finish(json.dumps({"success":0,"message":u"文件已经存在，请检查"}))
            return
        fr=base64.b64decode(obj['content'])
        md5code=md5.new(fr).hexdigest()
        if obj['md5']!=md5code:
            self.finish(json.dumps({"success":0,"message":u"提交的内容和校验码不一致，请检查"}))
            return
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        if saveToFile(saveFile,fr):
            self.finish(json.dumps({"success":1,"message":u"文件上传成功"}))   
        else:
            self.finish(json.dumps({"success":0,"message":u"文件上传失败"}))             

#删除文件，参数 filename
class DeleteHandler(tornado.web.RequestHandler):
    def post(self):
        filename = self.get_argument('filename')
        if filename.startswith('/'): filename='.'+filename    
        deleteFile = os.path.join(FileStoragePath,filename)
        checkAcess(deleteFile)
        if not os.path.exists(deleteFile):
            raise tornado.web.HTTPError(404, u"需要删除的文件不存在")
        os.remove(deleteFile)
        self.finish(u"文件删除成功")

#API 删除文件 
#参数 {"filename":"/xxx/xxx.png"}
#filename 需要删除的文件名
class APIDeleteHandler(tornado.web.RequestHandler):
    def post(self):
        obj = json_decode(self.request.body)  
        if not obj['filename']:
            self.finish(json.dumps({"success":0,"message":u"需要删除的文件名为空"}))
            return  
        filename=obj['filename']    
        if filename.startswith('/'): filename='.'+filename        
        deleteFile = os.path.join(FileStoragePath,filename)
        if not ajaxCheckAcess(self,deleteFile): return
        if not os.path.exists(deleteFile):
            self.finish(json.dumps({"success":0,"message":u"需要删除的文件不存在"}))
            return
        try:            
            os.remove(deleteFile)
            self.finish(json.dumps({"success":1,"message":u"文件删除成功"}))
        except:
            self.finish(json.dumps({"success":0,"message":u"文件删除失败"}))    

#文件列表， 参数 path
class ListHandler(tornado.web.RequestHandler):
    def post(self):
        path=self.get_argument('path')
        if path.startswith('/'): path='.'+path            
        savePath = os.path.join(FileStoragePath,path)
        checkAcess(savePath)
        if not os.path.exists(savePath):
            raise tornado.web.HTTPError(404, u"路径 %s 不存在."%path)
        self.finish(json.dumps(os.listdir(savePath)))

#API 文件列表
#参数 {"path":"/"}
#path 路径
class APIListHandler(tornado.web.RequestHandler):
    def post(self):
        obj = json_decode(self.request.body)  
        if not obj['path']:
            self.finish(json.dumps({"success":0,"message":u"路径为空"}))
            return  
        path= obj['path']   
        if path.startswith('/'): path='.'+path        
        path = os.path.join(FileStoragePath,path)
        if not ajaxCheckAcess(self,path): return

        if not os.path.exists(path):
            self.finish(json.dumps({"success":0,"message":u"路径不存在"}))
            return
        self.finish(json.dumps({"success":1,"message":os.listdir(path)}))

#MD5 参数 filename
class MD5Handler(tornado.web.RequestHandler):
    def post(self):
        filename = self.get_argument('filename')
        if filename.startswith('/'): filename='.'+filename        
        md5file = os.path.join(FileStoragePath,filename)
        checkAcess(md5file)
        if not os.path.exists(md5file):
            raise tornado.web.HTTPError(404, u"文件不存在")
        if not os.path.isfile(md5file):
            raise tornado.web.HTTPError(403, u"不是一个有效的文件")            
        self.finish(md5.new(open(md5file).read()).hexdigest())

#APIMD5
#参数 {"filename":"/xe/xxx.png"}
#file 需求获取MD5的文件
class APIMD5Handler(tornado.web.RequestHandler):
    def post(self):
        obj = json_decode(self.request.body)  
        if not obj['filename']:
            self.finish(json.dumps({"success":0,"message":u"文件名为空"}))
            return  
        filename=obj['filename']
        if filename.startswith('/'): filename='.'+filename        
        md5file = os.path.join(FileStoragePath,filename)
        if not ajaxCheckAcess(self,md5file): return
        if not os.path.exists(md5file):
            self.finish(json.dumps({"success":0,"message":u"文件不存在"}))
            return
        if not os.path.isfile(md5file):
            self.finish(json.dumps({"success":0,"message":u"不是一个有效的文件"}))
            return          
        self.finish(json.dumps({"success":1,"message":md5.new(open(md5file).read()).hexdigest()}))

#Info 参数 filename
class InfoHandler(tornado.web.RequestHandler):
    def post(self):
        filename = self.get_argument('filename')
        if filename.startswith('/'): filename='.'+filename        
        infofile = os.path.join(FileStoragePath,filename)
        checkAcess(infofile)
        if not os.path.exists(infofile):
            raise tornado.web.HTTPError(404, u"文件不存在")
        if not os.path.isfile(infofile):
            raise tornado.web.HTTPError(403, u"不是一个有效的文件")

        self.finish(json.dumps(getFileInfo(infofile)))

#APIInfo
#参数 {"filename":"/xe/xxx.png"}
#file 需要获取信息的文件或目录
class APIInfoHandler(tornado.web.RequestHandler):
    def post(self):
        obj = json_decode(self.request.body)  
        if not obj['filename']:
            self.finish(json.dumps({"success":0,"message":u"文件名为空"}))
            return  
        filename=obj['filename']
        if filename.startswith('/'): filename='.'+filename        
        infofile = os.path.join(FileStoragePath,filename)
        if not ajaxCheckAcess(self,infofile): return
        if not os.path.exists(infofile):
            self.finish(json.dumps({"success":0,"message":u"文件不存在"}))
            return
        if not os.path.isfile(infofile):
            self.finish(json.dumps({"success":0,"message":u"不是一个有效的文件"}))
            return          
        self.finish(json.dumps({"success":1,"message":getFileInfo(infofile)}))

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/download/(.*)",tornado.web.StaticFileHandler, {"path": FileStoragePath},),
    (r"/api/download/",APIDownloadHandler),
    (r"/upload/",UploadHandler),
    (r"/api/upload/",APIUploadHandler),
    (r"/delete/",DeleteHandler),
    (r"/api/delete/",APIDeleteHandler),
    (r"/list/",ListHandler),
    (r"/api/list/",APIListHandler),
    (r"/md5/",MD5Handler),
    (r"/api/md5/",APIMD5Handler),
    (r"/info/",InfoHandler),
    (r"/api/info/",APIInfoHandler),
])

if __name__ == "__main__":
    port = 8888
    print("Start File Server on Port %s"%port)
    application.listen(port)
    tornado.ioloop.IOLoop.current().start()

