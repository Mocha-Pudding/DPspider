#coding:utf-8
import os
import json
from settings import *
from util.dianping import *

def recover(kind,url,path):
    def outwrapper(func):
        def wrapper(self,*args,**kwargs):
            if kwargs.get('reget'):
                res = eval(DIANPING_FUNC[kind])(self.session,url)
                setattr(self,kind,res)
                with open(path,'w') as f:
                    f.write(json.dumps(getattr(self,kind)))
            else:
                if os.path.isfile(path):
                    with open(path,'r') as f:
                        b = f.read()
                    if b:
                        setattr(self, kind, json.loads(b))
                        return getattr(self,kind)
            res = func(self,*args,**kwargs)
            with open(path,'w') as f:
                f.write(json.dumps(res))
            return res
        return wrapper
    return outwrapper