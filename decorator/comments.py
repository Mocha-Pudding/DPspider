#coding:utf-8

def more_than(pageCount):
    def outwrapper(func):
        def wrapper(self,*args,**kwargs):
            more = self.get_reviews_pages_count()
            if more and more != None and more >= pageCount:
                self.more_page = more
                return func(self,*args,**kwargs)
            else:
                return
        return wrapper
    return outwrapper
