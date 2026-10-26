import logging
import re

import requests
from fastapi import HTTPException, status
from sentence_transformers import SentenceTransformer
from sqlalchemy import and_, select
from sqlalchemy.orm import joinedload, selectinload

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
                filter_dict[next(iter(value.keys()))] = [str(i.strip()).lower()
                                        for i in re.split(r',', value[next(iter(value.keys()))]) if i]
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
            name_req = select(Models.Project.name).where(Models.Project.name == data['Проект'])
            if not db.execute(name_req).scalars().one_or_none():
                scope_req = select(Models.Scope.name).where(Models.Scope.name == data['Направление'])
                if not db.execute(scope_req).scalars().one_or_none() and data['Направление']:
                    add_scope = Models.Scope(name=data['Направление'])
                    db.add(add_scope)
                    db.flush()
                stage_req = select(Models.Stage.name).where(Models.Stage.name == data['Стадия'])
                if not db.execute(stage_req).scalars().one_or_none() and data['Стадия']:
                    add_stage = Models.Stage(name=data['Стадия'])
                    db.add(add_stage)
                    db.flush()

                scope_id_req = db.execute(select(Models.Scope.id).where(Models.Scope.name == data['Направление'])).scalars().one_or_none()
                stage_id_req = db.execute(select(Models.Stage.id).where(Models.Stage.name == data['Стадия'])).scalars().one_or_none()
                project_req = Models.Project(name=data['Проект'], description=' '.join(data['Краткое описание']), stage_id=stage_id_req, scope_id=scope_id_req)
                db.add(project_req)
                db.flush()
                if data['Ключевые факты']:
                    for fact in data['Ключевые факты']:
                        add_fact = Models.Key_fact(text=fact, embedding=model.encode(fact.lower()),project_id=project_req.id)
                        db.add(add_fact)
                        db.flush()
                
                if data['Источник']:
                    for link in data['Источник']:
                        link_req = select(Models.Link.name).where(Models.Link.name == link)
                        if not db.execute(link_req).scalars().one_or_none():
                            add_link = Models.Link(name=link)
                            db.add(add_link)
                            db.flush()
                            add_middle_project_link = Models.Middle_project_link(project_id=project_req.id, link_id=add_link.id)
                            db.add(add_middle_project_link)
                            db.flush()
                        else:
                            link_id_req = db.execute(select(Models.Link.id).where(Models.Link.name == link)).scalars().one_or_none()
                            add_middle_project_link = Models.Middle_project_link(project_id=project_req.id, link_id=link_id_req)
                            db.add(add_middle_project_link)
                            db.flush()
                participants_dict = utils.extract_participant_country(list(data.keys()), data)
                if participants_dict.keys():
                    for country in participants_dict.keys():
                        country_req = select(Models.Country.name).where(Models.Country.name == country)
                        if not db.execute(country_req).scalars().one_or_none():
                            add_country = Models.Country(name=country)
                            db.add(add_country)
                            db.flush()
                        country_id_req = db.execute(select(Models.Country.id).where(Models.Country.name == country)).scalars().one_or_none()
                        if participants_dict[country]:
                            for participant in participants_dict[country]:
                                participant_req = select(Models.Participant.name).where(Models.Participant.name == participant)
                                if not db.execute(participant_req).scalars().one_or_none():
                                    add_participant = Models.Participant(name=participant, country_id=country_id_req)
                                    db.add(add_participant)
                                    db.flush()
                                    add_middle_project_participant = Models.Middle_project_participant(project_id=project_req.id, participant_id=add_participant.id)
                                    db.add(add_middle_project_participant)
                                    db.flush()
                                else:
                                    participant_id_req = db.execute(select(Models.Participant.id).where(Models.Participant.name == participant)).scalars().one_or_none()
                                    add_middle_project_participant = Models.Middle_project_participant(project_id=project_req.id, participant_id=participant_id_req)
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
        results_list = []
        search_limit = int(config.get_origins_request_limit())
        emb_query = model.encode(query.lower())

        
        vec_response = utils.vector_serch(emb_query, search_limit, db)
        bm25_response = utils.bm25_search(query, search_limit, db)

        results_list.extend(vec_response)
        results_list.extend(bm25_response)
        
        fused = utils.RRF(results_list, search_limit)
        top = utils.rerank(query, fused, k)
        top_req = (
                select(Models.Project).where(Models.Project.id.in_(top))
        )
        context = "\n\n".join(f"[{number}] 'Project name': {item.name}, 'Project description': {item.description}" for number, item in enumerate(db.execute(top_req).scalars().unique().all()))
        
        
        messages = config.create_payload(query, context)
        tags_extraction_request = requests.post(config.get_ollama_api_url(), json=messages)

        if tags_extraction_request.status_code == 200:
            response = tags_extraction_request.json()
            logging.info(response['message']['content'])
            return response['message']['content']

         
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


async def get_preloaded_data(db):
    try:
        preloaded_data_request = (db.execute(select(Models.Project)))
        if preloaded_data_request.scalars().unique().all():
            return [[{'value': item, 'label': item} for item in (db.execute(select(Models.Project.name))).scalars().unique().all() if item], 
                    # [item for item in (db.execute(select(Models.GQW_model.reference))).scalars().unique().all() if item], 
                    [{'value':item, 'label':item} for item in (db.execute(select(Models.Scope.name))).scalars().unique().all() if item], 
                    [{'value':item, 'label':item} for item in (db.execute(select(Models.Stage.name))).scalars().unique().all() if item], 
                    [{'value':item, 'label':item} for item in (db.execute(select(Models.Participant.name))).scalars().unique().all() if item], ]
                    # [{'value':item, 'label':item} for item in (db.execute(select(Models.GQW_tag.tag_name))).scalars().unique().all() if item if item not in ['Нет доступных тэгов', 'There is no text', 'null']]]
        else:
            return [[{'value': 'No data', 'label': 'No data'}],
                    # ['No data',],
                    [{'value': 'No data', 'label': 'No data'}],
                    [{'value': 'No data', 'label': 'No data'}],
                    # [{'value': 'No data', 'label': 'No data'}],
                    [{'value': 'No data', 'label': 'No data'}]]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Sorry, the server is not available. The error is {e}')