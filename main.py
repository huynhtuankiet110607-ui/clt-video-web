from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
app = FastAPI(title="Mo phong CLT")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
return templates.TemplateResponse(
request=request, name="index.html", context={}
)
@app.get("/health")
async def health():
return {"status": "ok"}