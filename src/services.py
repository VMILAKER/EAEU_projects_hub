import src.utilities as utils
import logging

from fastapi import HTTPException, status

logging.getLogger().setLevel(logging.INFO)


async def get_projects(project_name, direction, stage, participants, db):
    try:
        pass
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Sorry, the server is not available. The error is {e}')


async def upload_projects(file, db):
    try:
        df = utils.load_df(file.filename, file.file)
        return df.head(5)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Sorry, the server is not available. The error is {e}')
