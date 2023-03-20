from fastapi import HTTPException,status,Response,Depends,APIRouter
from typing import List,Optional
from sqlalchemy.orm import Session
from .. import models,schemas,oauth2
from ..database import get_db
from sqlalchemy import func

router = APIRouter(
    prefix="/blogs",
    tags=["Blog"]
)


@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
            Limit: int = 15, skip:int = 0, search: Optional[str]= ""): 
    # cursor.execute("""SELECT * FROM blogs""")
    # posts = cursor.fetchall()

    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(Limit).offset(skip).all()
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(Limit).offset(skip).all()
    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(new_post:schemas.PostCreate, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO blogs(title,content,published) VALUES(%s, %s, %s) RETURNING * """,
    #                (new_post.title, new_post.content, new_post.published))
    # new_posts = cursor.fetchone()
    # conn.commit()
    new_posts = models.Post(owner_id=current_user.id, **new_post.dict())
    db.add(new_posts)
    db.commit()
    db.refresh(new_posts)
    return new_posts
    # post_dict = new_post.dict()
    # post_dict['id'] = randrange(0, 1000000)
    # my_posts.append(post_dict)
    # print(new_post.title)
    # print(new_post.content)
    # print(new_post.published)
    # print(new_post.rating)

    # return {"data": post_dict}

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id:int, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""Select * from blogs WHERE id = %s """, (int(id),))
    # post = cursor.fetchone()
    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post =  db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    
    return post 



@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int,db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM blogs WHERE id = %s returning *""", (str(id),))
    # index = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)

    index = post_query.first()
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    if index.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code= status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.PostResponse)
def update_posts(id:int, updated_post:schemas.PostCreate,db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):


    # cursor.execute("""UPDATE blogs SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """,
    #                (updated_post.title,updated_post.content,updated_post.published, str(id)))
    # index = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    index = post_query.first()

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} does not exist")
    
    if index.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return  post_query.first()