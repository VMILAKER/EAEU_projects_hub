import logging
import re
from uuid import UUID

import numpy as np
import pandas as pd
from fastapi import HTTPException, status
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

import src.models as Models
from config import (get_cross_encoder_name, get_statistics_form_template,
                    get_statistics_key_template)
from src.pydantic_models import Upload

reranker_name = get_cross_encoder_name()
reranker = CrossEncoder(reranker_name)

logging.getLogger().setLevel(logging.INFO)


def build_filter(filter_dict: dict) -> list:
    """The filter for dynamic search throughout database

    Args:
        filter_dict (dict): The dictationary of dynamic filters

    Returns:
        List: List of filters for the request
    """
    filters = []
    for key, value in filter_dict.items():
        if value and isinstance(value, list):
            filter_project_names = []
            filter_participants = []
            filter_scopes = []
            filter_stages = []
            for item in value:
                if key == 'project_name':
                    filter_project_names.append(
                        func.lower(Models.Project.name).like(f"%{item}%"))
                elif key == 'participants':
                    filter_participants.append(
                        func.lower(Models.Participant.name).like(f"%{item}%"))
                elif key == 'scope':
                    filter_scopes.append(
                        func.lower(Models.Scope.name).like(f"%{item}%"))
                elif key == 'stage':
                    filter_stages.append(
                        func.lower(Models.Stage.name).like(f"%{item}%"))
            filters.append(or_(*filter_project_names))
            filters.append(or_(*filter_participants))
            filters.append(or_(*filter_scopes))
            filters.append(or_(*filter_stages))
    return filters


def load_df(filename, content):
    if filename.endswith('.csv'):
        return [dict(w) for _,w in pd.read_csv(content, encoding='utf-8').astype(
            object).replace({np.nan: None}).iterrows()]
    elif filename.endswith(('.xlsx','.xls')):
        return [dict(row) for _,row in pd.read_excel(content).astype(
            object).replace({np.nan: None}).iterrows()]
    elif filename.endswith('.json'):
        return [dict(w) for _,w in pd.read_json(content).astype(
            object).replace({np.nan: None}).iterrows()]
    else:
        raise ValueError('Unsupported file extension')


def process_data(data: list):
    for project in data:
        try:
            Upload(**project)
            yield {
                'Проект': re.split(r'\n', project['Проект'])[0].strip() if project['Проект'] else None,
                'Направление': project['Направление'].strip() if project['Направление'] else None,
                'Стадия': project['Стадия'].strip() if project['Стадия'] else None,
                'Российские участники': [re.sub(r'[;|\n]', '', i).strip() for i in re.split(r'\d+.', project['Российские участники']) if i] if project['Российские участники'] else None,
                'Белорусские участники': [re.sub(r'[;\n]', '', j).strip() for j in re.split(r'\d+.', project['Белорусские участники']) if j] if project['Белорусские участники'] else None,
                'Ключевые факты': [i.replace('\n', '').strip() for i in re.split(r'• ', project['Ключевые факты']) if i] if project['Ключевые факты'] else None,
                'Источник': [i.strip() for i in re.findall('https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)', project['Источник']) if i] if project['Источник'] else None,
                'Краткое описание': [i.replace('\n', '').strip() for i in re.split(r'• ', project['Краткое описание']) if i] if project['Краткое описание'] else None,
            }
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={e})

         

def extract_participant_country(countries, data:dict):
    participants_of_countries_dict = {}
    for country in countries:
        if 'рос' in country.lower():
            participants_of_countries_dict[Models.CountryTemplates.RUSSIA.value]= data[country]
        elif 'белорус' in country.lower():
            participants_of_countries_dict[Models.CountryTemplates.BELARUS.value]= data[country]
        elif 'кыргыз' in country.lower():
            participants_of_countries_dict[Models.CountryTemplates.KYRGYZSTAN.value]= data[country]
        elif 'казах' in country.lower():
            participants_of_countries_dict[Models.CountryTemplates.KAZAKHSTAN.value]= data[country]
        elif 'арм' in country.lower():
            participants_of_countries_dict[Models.CountryTemplates.ARMENIA.value]= data[country]
    return participants_of_countries_dict


def count_by_dict_key(data):
    final_report_dict = {}
    
    if isinstance(data, list):
        for i in data:
            for key in i.keys():
                key_template = get_statistics_key_template(key)
                if isinstance(i[key], str):
                    final_report_dict.update(get_statistics_form_template(final_report_dict, key_template, i[key]))
                elif isinstance(i[key], list):
                    for value in i[key]:
                        if isinstance(value, dict):
                            final_report_dict.update(get_statistics_form_template(final_report_dict, 'Распределение по странам' , next(iter(value.keys()))))
                            final_report_dict.update(get_statistics_form_template(final_report_dict, 'Распределение по компаниям' , next(iter(value.values()))))       
                        elif isinstance(value, str):
                            final_report_dict.update(get_statistics_form_template(final_report_dict, key_template, value))
    return final_report_dict


def vector_serch(emb_query, search_limit:int, db):
    vector_req = (
        select(Models.Project).join(Models.Project.key_facts_relation)
        .options( 
            joinedload(Models.Project.key_facts_relation)
        ).order_by(Models.Key_fact.embedding.cosine_distance(emb_query)).limit(search_limit)
    )
    return [{'project_id': str(i.id), 'content': j.text} for i in db.execute(vector_req).scalars().unique().all()  for j in i.key_facts_relation]


def bm25_search(query:str, search_limit:int, db):
    bm25_req = (
        select(Models.Project).join(Models.Project.key_facts_relation)
        .options( 
            joinedload(Models.Project.key_facts_relation)
        )
    )

    rows = [{'project_id': str(i.id), 'content': j.text} for i in db.execute(bm25_req).scalars().unique().all() for j in i.key_facts_relation]
    bm25 = BM25Okapi([r['content'].lower().split() for r in rows])
    scores = bm25.get_scores(query.lower().split())
    ranked = sorted(zip(rows, scores), key=lambda x: x[1], reverse=True)
    return[r for r, _ in ranked[:search_limit]]

    
def RRF(results_list: list, search_limit: int):
    scores, docs = {}, {}
    for rank, results in enumerate(results_list):
        project_id = results['project_id']
        content = results['content']
        scores[project_id] = 1 / (search_limit + rank + 1)
        docs[project_id] = content
    return [(i, docs[i]) for i in sorted(scores, key=scores.get, reverse=True)]


def rerank(query, candidates:list, top_n:int):
    scores = reranker.predict([(query, c[1]) for c in candidates])
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return [UUID(c[0]) for c, _ in ranked[:top_n]]               
