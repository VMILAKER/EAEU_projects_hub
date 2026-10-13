import logging
import re

from fastapi import HTTPException, status
from sentence_transformers import SentenceTransformer
from sqlalchemy import and_, select
from sqlalchemy.orm import joinedload, selectinload
import requests

import config
import src.models as Models
import src.utilities as utils

logging.getLogger().setLevel(logging.INFO)

model_name = config.get_sentence_transformer_model_name()
model = SentenceTransformer(model_name)

async def get_projects(project_name, scope, stage, participants, db):
    try:
        filter_dict = {}
        for value in [{'project_name': project_name}, {'scope': scope}, {'stage': stage}, {'participants':participants}]:
            if list(value.values())[0]:
                filter_dict[list(value.keys())[0]] = [str(i.strip()).lower()
                                        for i in re.split(r',', value[list(value.keys())[0]]) if i]
        stmt = (
            select(Models.Project).join(Models.Project.scope_relation)
            .join(Models.Project.link_relation).join(Models.Project.key_facts_relation)
            .join(Models.Project.stage_relation).join(Models.Project.participant_relation)
            .options(
                joinedload(Models.Project.scope_relation),          
                joinedload(Models.Project.stage_relation),    
                joinedload(Models.Project.link_relation),     
                selectinload(Models.Project.participant_relation)
                    .joinedload(Models.Participant.country_relation),  
                selectinload(Models.Project.key_facts_relation)
            )
        ).where(and_(*utils.build_filter(filter_dict)))

        if db.execute(stmt).scalars().first():
            return [
                {
                'project_name': i.name,
                'scope': i.scope_relation.name,
                'stage': i.stage_relation.name,
                'participants': [{f'{j.country_relation.name}': j.name} for j in i.participant_relation],
                'key_facts': '; '.join([j.text for j in i.key_facts_relation]),
                'description': i.description,
                'links': [j.name for j in i.link_relation]
                } for i in db.execute(stmt).scalars().unique().all()
            ]
        else:
            return 'No matches'
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Sorry, the server is not available. The error is {e}')


async def upload_projects(file, db):
    try:
        df = utils.load_df(file.filename, file.file)
        processed_df = list(utils.process_data(df))
        duplicate_list =[]
        for data in processed_df:
            if not db.query(Models.Project.name).filter(Models.Project.name == data['Проект']).one_or_none():
                if not db.query(Models.Scope.name).filter(Models.Scope.name == data['Направление']).one_or_none() and data['Направление']:
                    add_scope = Models.Scope(name=data['Направление'])
                    db.add(add_scope)
                    db.flush()
                if not db.query(Models.Stage.name).filter(Models.Stage.name == data['Стадия']).one_or_none() and data['Стадия']:
                    add_stage = Models.Stage(name=data['Стадия'])
                    db.add(add_stage)
                    db.flush()

                scope_id_req = db.query(Models.Scope.id).filter(Models.Scope.name == data['Направление']).one_or_none()
                stage_id_req = db.query(Models.Stage.id).filter(Models.Stage.name == data['Стадия']).one_or_none()
                project_req = Models.Project(name=data['Проект'], description=' '.join(data['Краткое описание']), stage_id=stage_id_req.id, scope_id=scope_id_req.id)
                db.add(project_req)
                db.flush()
                if data['Ключевые факты']:
                    for fact in data['Ключевые факты']:
                        logging.info(fact)
                        add_fact = Models.Key_fact(text=fact, embedding=model.encode(fact.lower()),project_id=project_req.id)
                        db.add(add_fact)
                        db.flush()
                
                if data['Источник']:
                    for link in data['Источник']:
                        logging.info(link)
                        if not db.query(Models.Link.name).filter(Models.Link.name == link).one_or_none():
                            add_link = Models.Link(name=link)
                            db.add(add_link)
                            db.flush()
                            add_middle_project_link = Models.Middle_project_link(project_id=project_req.id, link_id=add_link.id)
                            db.add(add_middle_project_link)
                            db.flush()
                        else:
                            link_id_req = db.query(Models.Link.id).filter(Models.Link.name == link).one_or_none()
                            add_middle_project_link = Models.Middle_project_link(project_id=project_req.id, link_id=link_id_req.id)
                            db.add(add_middle_project_link)
                            db.flush()
                participants_dict = utils.extract_participant_country(list(data.keys()), data)
                # logging.info(participants_dict)
                if participants_dict.keys():
                    for country in participants_dict.keys():
                        logging.info(country)
                        if not db.query(Models.Country.name).filter(Models.Country.name == country).one_or_none():
                            add_country = Models.Country(name=country)
                            db.add(add_country)
                            db.flush()
                        country_id_req = db.query(Models.Country.id).filter(Models.Country.name == country).one_or_none()
                        if participants_dict[country]:
                            for participant in participants_dict[country]:
                                logging.info(participant)
                                if not db.query(Models.Participant.name).filter(Models.Participant.name == participant).one_or_none():
                                    add_participant = Models.Participant(name=participant, country_id=country_id_req.id)
                                    db.add(add_participant)
                                    db.flush()
                                    add_middle_project_participant = Models.Middle_project_participant(project_id=project_req.id, participant_id=add_participant.id)
                                    db.add(add_middle_project_participant)
                                    db.flush()
                                else:
                                    participant_id_req = db.query(Models.Participant.id).filter(Models.Participant.name == participant).one_or_none()
                                    add_middle_project_participant = Models.Middle_project_participant(project_id=project_req.id, participant_id=participant_id_req.id)
                                    db.add(add_middle_project_participant)
                                    db.flush()
                db.commit()
            else:
                duplicate_list.append(f'{data['Проект']}')
        return f'Data from {file.filename} is uploaded, Duplicates: {duplicate_list}\n'
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Sorry, the server is not available. The error is {e}')

async def get_projects_by_query(query, k, db):
    try:
        origins ='rrtrt'
        messages = config.create_payload(query, origins)
        tags_extraction_request = requests.post(config.get_ollama_api_url(), json=messages)
        # tags_extraction_request = requests.post(config.get_ollama_api_url(),json=messages)
        if tags_extraction_request.status_code == 200:
            return tags_extraction_request.json()
        # return tags_extraction_request
         
    except Exception as e:
        raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Sorry, the server is not available. The error is {e}')


async def describe_data(db):
    try:
        stmt = (
            select(Models.Project).join(Models.Project.scope_relation)
            .join(Models.Project.link_relation).join(Models.Project.key_facts_relation)
            .join(Models.Project.stage_relation).join(Models.Project.participant_relation)
            .options(
                joinedload(Models.Project.scope_relation),          
                joinedload(Models.Project.stage_relation),    
                joinedload(Models.Project.link_relation),     
                selectinload(Models.Project.participant_relation)
                    .joinedload(Models.Participant.country_relation),  
                selectinload(Models.Project.key_facts_relation)
            )
        )

        if db.execute(stmt).scalars().first():
            data = [
                {
                # 'project_name': i.name,
                'scope': i.scope_relation.name,
                'stage': i.stage_relation.name,
                'participants': [{f'{j.country_relation.name}': j.name} for j in i.participant_relation],
                # 'key_facts': '; '.join([j.text for j in i.key_facts_relation]),
                # 'description': i.description,
                'links': [j.name for j in i.link_relation]
                } for i in db.execute(stmt).scalars().unique().all()
            ]
            return utils.count_by_dict_key(data)
        else:
            return 'No data in database'
    except Exception as e:
        raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Sorry, the server is not available. The error is {e}')