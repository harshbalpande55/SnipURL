from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.openapi.utils import get_openapi
from app.backend import crud,models
from app.backend.schemas import URLBase,URLInfo
from app.backend.config import get_settings
from sqlalchemy.orm import Session
from app.backend.database import SessionLocal, engine
from starlette.datastructures import URL
import validators

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_admin_info(db_url: models.URL) -> URLInfo:
    base_url = URL(get_settings().base_url)

    admin_endpoint = app.url_path_for(
        "administration info", secret_key=db_url.secret_key
    )

    db_url.url = str(base_url.replace(path=db_url.key))
    db_url.admin_url = str(base_url.replace(path=admin_endpoint))
    return db_url

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Url Shortener API's",
        version="2.5.0",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

def raise_not_found(request):
    message = f"URL '{request.url}' doesn't exist"
    raise HTTPException(status_code=404, detail=message)

def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)

app = FastAPI()
app.openapi = custom_openapi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost","http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
models.Base.metadata.create_all(bind=engine)


@app.post("/url",response_model=URLInfo)
def create_url(url: URLBase, db: Session = Depends(get_db)):
    if not validators.url(url.target_url):
        raise_bad_request(message="Your provided URL is not valid")
    
    db_url = crud.create_db_url(db=db, url=url)
    return get_admin_info(db_url)

@app.get("/{url_key}")
def forward_to_target_url(url_key:str, request: Request, db: Session = Depends(get_db)):

    if db_url := crud.get_db_url_by_key(db=db, url_key=url_key):
        crud.update_db_clicks(db=db, db_url=db_url)
        return RedirectResponse(db_url.target_url)
    else:
        raise_not_found(request)

@app.get("/admin/{secret_key}", name="administration info", response_model=URLInfo)
def get_url_info(secret_key: str, request: Request, db: Session = Depends(get_db)):
    if db_url := crud.get_db_url_by_secret_key(db, secret_key=secret_key):
        return get_admin_info(db_url)
    else:
        raise_not_found(request)
        
@app.post("/admin/{secret_key}")
def disable_url(
    secret_key: str, request: Request, db: Session = Depends(get_db)
):
    if db_url := crud.deactivate_db_url_by_secret_key(db, secret_key=secret_key):
        message = f"Successfully deleted shortened URL for '{db_url.target_url}'"
        return {"detail": message}
    else:
        raise_not_found(request)
