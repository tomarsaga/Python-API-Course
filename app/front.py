from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import blog,user,auth,vote
from .config import settings

print(settings.database_username)

models.Base.metadata.create_all(bind=engine)

dev = FastAPI()

# origins = ["https://www.google.com", "https://www.youtube.com"]
origins = ["*"]

dev.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


my_posts = [{"title":"IPL","content":"BCCI","id":1}, {"title":"BBL","content":"ACB","id":2}]

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p
        
def find_index_post(id):
    for i,p in enumerate(my_posts):
        if p['id'] ==id:
            return i
        
dev.include_router(blog.router)
dev.include_router(user.router)
dev.include_router(auth.router)
dev.include_router(vote.router)



@dev.get("/")
def getUser():
    return {"data":my_posts}


