# crud.py (MongoDB/Async Edition)

from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any

from . import schemas
from datetime import datetime

PAGE_COLLECTION = "pages"
POST_COLLECTION = "posts"

async def create_page(db: AsyncIOMotorDatabase, page_data: schemas.PageCreate):
    
    page_doc: Dict[str, Any] = page_data.model_dump(exclude={"posts_data", "employee_data"})
    page_doc["scrape_timestamp"] = datetime.utcnow()
    
    existing_page = await db[PAGE_COLLECTION].find_one({"page_id": page_doc["page_id"]})
    if existing_page:
        raise ValueError("Page ID already exists.")
        
    await db[PAGE_COLLECTION].insert_one(page_doc)
    
    post_documents = []
    for post_data in page_data.posts_data:
        post_doc = post_data.model_dump()
        post_doc["page_id"] = page_data.page_id # Foreign key reference
        post_documents.append(post_doc)
        
    if post_documents:
        await db[POST_COLLECTION].insert_many(post_documents)

    return await get_page_by_page_id(db, page_data.page_id)

async def get_page_by_page_id(db: AsyncIOMotorDatabase, page_id: str):
    document = await db[PAGE_COLLECTION].find_one({"page_id": page_id})
    if document:
        document['id'] = str(document.pop('_id')) 
        return document
    return None

async def get_pages_list(
    db: AsyncIOMotorDatabase, 
    skip: int = 0, 
    limit: int = 10,
    min_followers: Optional[int] = None,
    name_search: Optional[str] = None
) -> List[Dict[str, Any]]:
   
    query: Dict[str, Any] = {}
    
    if min_followers is not None:
        query["total_followers"] = {"$gte": min_followers}
        
    if name_search:
        query["name"] = {"$regex": name_search, "$options": "i"} # "i" for case insensitive

    cursor = db[PAGE_COLLECTION].find(query).skip(skip).limit(limit)
    
    pages = []
    async for doc in cursor:
        doc['id'] = str(doc.pop('_id'))
        pages.append(doc)
        
    return pages

async def get_page_posts(db: AsyncIOMotorDatabase, page_id: str, skip: int = 0, limit: int = 15):
    cursor = db[POST_COLLECTION].find({"page_id": page_id}).sort("timestamp", -1).skip(skip).limit(limit)
    
    posts = []
    async for doc in cursor:
        doc['id'] = str(doc.pop('_id'))
        posts.append(doc)
        
    return posts