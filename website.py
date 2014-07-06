import sqlalchemy as sql

import tornado.ioloop
import tornado.web
import tornado
import os
import random

import uuid
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import dogecoinrpc
Base = declarative_base()
from sqlalchemy import Column, String,Float, Boolean 
def generate_URL(ending):
    url= "http://localhost:8080/"
    return url+ending
    
def create_session():

        engine = sql.create_engine("sqlite:///multisig.db")
        Session = sessionmaker(bind=engine)
        session =Session()
        return session
        
class multi (Base):
    __tablename__ = "Multi"
    ID = Column(String, primary_key=True)
    pub1 = Column(String)
    pub2 = Column(String)
    pub3 = Column(String)
    multi_address = Column(String)
    redeem_script = Column(String)


    
    
    
    
    def __repr__(self):
        return "<ID = '%s',multi_address= '%s'>" \
        % (self.ID,self.multi_address)
        
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")
    def post(self):
        session = create_session()
        key1 = self.get_argument("key1")
        ID  = str(uuid.uuid4())
        dbadd = multi(ID = ID, pub1 = key1)
        session.add(dbadd)
        print dbadd
        session.commit()
        self.redirect("address/?ID="+ID)
        
class AddressHandler(tornado.web.RequestHandler):
    def get(self):
        ID = self.get_argument("ID")
        session = create_session()
        search= session.query(multi).filter(multi.ID==ID).first()
        if search.multi_address:
            self.render("address2.html",pub1= search.pub1,ID=ID, pub2 = search.pub2,\
            pub3 = search.pub3, madd = search.multi_address, redeem = search.redeem_script)
        else:
            self.render("address.html",pub1= search.pub1,ID=ID, pub2 = search.pub2,\
            pub3 = search.pub3, madd = search.multi_address, redeem = search.redeem_script)
        session.close()
    def post(self):
        ID = self.get_argument("ID")
        session = create_session()
        search= session.query(multi).filter(multi.ID==ID).first()
        try:
            key2 = self.get_argument("key2")
            if len(key2)==34:
                search.pub2=key2
        except:
            pass
        try:    
            key3 = self.get_argument("key3")
            if len(key3)==34:
                print "key3 ", key3
                search.pub3=key3

        except:
            pass
        session.add(search)
        session.commit()
        session = create_session()
        search= session.query(multi).filter(multi.ID==ID).first()
        if search.pub1 and search.pub2 and search.pub3 and search.multi_address== None:
            multi_add =  doge.createmultisig(2,[search.pub1,search.pub3,search.pub2])
            print multi_add
            search.multi_address = multi_add["address"]
            search.redeem_script =multi_add["redeemScript"]
        session.add(search)
        session.commit()
        self.redirect("/address/?ID="+ID)
                

STATIC_PATH= os.path.join(os.path.dirname(__file__),r"static/")       
application = tornado.web.Application([
	(r"/", MainHandler),
	(r"/address/", AddressHandler),
	
],static_path=STATIC_PATH,login_url=r"/login/", debug=True,
 cookie_secret="35wfa35tgtres5wf5tyhxbt4"+str(random.randint(0,1000000)))
if __name__ == "__main__":
    doge = dogecoinrpc.connect_to_local()
    engine = sql.create_engine("sqlite:///multisig.db")
    Base.metadata.create_all(engine) 

    Session = sessionmaker(bind=engine)
    session = Session()
    session.commit()

    
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
    
