import uvicorn
from fastapi import FastAPI

from config import get_frontend_url
from src import routers

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.include_router(routers.router, prefix='/eaeu_hub')


origins = get_frontend_url()
app.add_middleware(CORSMiddleware, allow_origins=origins,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


if __name__ == '__main__':
    uvicorn.run(app='main:app', host='0.0.0.0',
                port=8000, reload=True, workers=3)
