# routers/insights.py (Async/MongoDB Update)

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase # Use the async database type
from typing import List, Optional

from .. import crud, schemas 
from ..database import get_db_async 
from ..scraper import LinkedInScraper

router = APIRouter(
    prefix="/pages",
    tags=["insights"]
)

scraper = LinkedInScraper()

@router.get("/{page_id}", response_model=schemas.Page)
async def get_page_details(
    page_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db_async) # Use async dependency
):
    db_page_doc = await crud.get_page_by_page_id(db, page_id=page_id)
    
    if db_page_doc:
        page = schemas.Page(**db_page_doc) 
        
        page.recent_posts = await crud.get_page_posts(db, page_id=page_id, limit=10)
        return page

    print(f"Page not found in DB. Attempting scrape for: {page_id}")
    scraped_data = scraper.scrape_page(page_id) 
    
    if not scraped_data:
        raise HTTPException(status_code=404, detail=f"Page ID '{page_id}' not found and scraping failed.")

    try:
        db_page_doc = await crud.create_page(db, page_data=scraped_data)
        page = schemas.Page(**db_page_doc) 
        page.recent_posts = await crud.get_page_posts(db, page_id=page_id, limit=10)
        return page
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save scraped data: {e}")


@router.get("/", response_model=List[schemas.Page])
async def get_filtered_pages(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=50),
    min_followers: Optional[int] = Query(None, ge=0),
    name_search: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db_async)
):
    pages_list = await crud.get_pages_list(
        db, 
        skip=skip, 
        limit=limit,
        min_followers=min_followers,
        name_search=name_search,
    )
    return [schemas.Page(**p) for p in pages_list]

@router.get("/{page_id}/posts", response_model=List[schemas.Post])
async def get_posts_for_page(
    page_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(15, le=50),
    db: AsyncIOMotorDatabase = Depends(get_db_async)
):
    if not await crud.get_page_by_page_id(db, page_id):
        raise HTTPException(status_code=404, detail="Page not found.")
        
    posts = await crud.get_page_posts(db, page_id=page_id, skip=skip, limit=limit)
    return [schemas.Post(**p) for p in posts]