from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from urllib.parse import urlparse
from app.scraper import fetch_links, scrape_content, extract_unique_categories, extract_unique_pages
from app.schemas import UrlResponse, ContentResponse

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str

class URLListRequest(BaseModel):
    urls: list[str]

class CategoryLink(BaseModel):
    category: str
    link: str

class PageLink(BaseModel):
    category: str
    link: str

class UrlResponse(BaseModel):
    urls: list[str]
    categories: list[CategoryLink]
    pages: list[PageLink]

class ContentResponse(BaseModel):
    contents: dict

@app.post("/analyze", response_model=UrlResponse)
async def analyze_url(request: URLRequest):
    try:
        # Parse the domain from the provided URL
        parsed_url = urlparse(request.url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # Fetch links from the main URL
        urls = await fetch_links(request.url)
        
        # Extract unique categories from the URLs
        categories = extract_unique_categories(urls)

        # Generate category links
        category_links = [
            {'category': cat['category'], 'link': cat['link']}
            for cat in categories
        ]

        # Extract unique pages from the URLs
        pages = extract_unique_pages(urls)
        page_links = [
            {'category': page['category'], 'link': page['link']}
            for page in pages
        ]
        
        return {
            "urls": urls,
            "categories": category_links,
            "pages": page_links
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape", response_model=ContentResponse)
async def scrape_urls(request: URLListRequest):
    try:
        contents = await scrape_content(request.urls)
        return {"contents": contents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
