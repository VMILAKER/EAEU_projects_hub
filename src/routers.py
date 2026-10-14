from fastapi import (APIRouter, Depends, File, Header, HTTPException,
                     UploadFile, status)
from sqlalchemy.orm import Session

import config
import src.services as Service
from src.database import get_db_sql


async def verify_internal_api_key(
    x_internal_api_key: str | None = Header(None, alias='API_Key'),
) -> bool:
    internal_api_key = config.get_backend_api_key()

    if not x_internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Internal backend API key is missing',
        )

    if not internal_api_key or x_internal_api_key != internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid internal backend API key',
        )
    return True


router = APIRouter(
    dependencies=[Depends(verify_internal_api_key)],
    responses={
        401: {'description': 'Invalid or missing internal API key'},
    },
)


@router.get('/get_projects', tags=['get_node'])
async def get(project_name: str = None, scope: str = None, stage: str = None, participants: str = None, db: Session = Depends(get_db_sql)):
    return await Service.get_projects(project_name, scope, stage, participants, db)


@router.post('/upload_projects', tags=['upload_node'])
async def post(file: UploadFile = File(...), db: Session = Depends(get_db_sql)):
    return await Service.upload_projects(file, db)


@router.get('/get_projects_by_query', tags=['get_node'])
async def get_by_query(query: str = 'Создание АЭС', top_K: int = 5, db: Session = Depends(get_db_sql)):
    return await Service.get_projects_by_query(query, top_K, db)

@router.get('/statistics', tags=['statistics'])
async def get_statistics(db: Session = Depends(get_db_sql)):
    return await Service.describe_data(db)
