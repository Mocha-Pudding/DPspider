#coding:utf-8

def init_db(db):
    if db and not db.connected:
        db.connect()
    return db

def not_has_class_li(tag):
    return not tag.has_attr('class') and tag.name == 'li'