import logging
import re
from typing import List
from uuid import UUID

import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import joinedload, selectinload

import src.models as Models
from config import get_cross_encoder_name

reranker = CrossEncoder(get_cross_encoder_name())
logging.getLogger().setLevel(logging.INFO)


def build_filter(filter_dict: dict) -> List:
    """The filter for dynamic search throughout database

    Args:
        filter_dict (dict): The dictationary of dynamic filters

    Returns:
        List: List of filters for the request
    """
    filters = []
    for key in filter_dict.keys():
        if filter_dict[key]:
            if isinstance(filter_dict[key], list):
                filter_project_names = []
                filter_participants = []
                filter_scopes = []
                filter_stages = []
                for item in filter_dict[key]:
                    logging.info(item)
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
                            func.lower(Models.Stages.name).like(f"%{item}%"))
                filters.append(or_(*filter_project_names))
                filters.append(or_(*filter_participants))
                filters.append(or_(*filter_scopes))
                filters.append(or_(*filter_stages))
            # else:
            #     logging.info(1)
            #     if key == 'project_name':
            #         filters.append(
            #             Models.Project.name.icontains(filter_dict[key]))
            #     elif key == 'participants':
            #         filters.append(
            #             func.lower(getattr(Models.Participant, 'name')) == filter_dict[key])
            #     elif key == 'scope':
            #         filters.append(
            #             func.lower(Models.Scope.name).like(f"%{func.lower(filter_dict[key])}%"))
            #     elif key == 'stage':
            #         filters.append(
            #             func.lower(Models.Stage.name.icontains(filter_dict[key])))
    return filters


def load_df(filename, content):
    if (filename).endswith('.csv'):
        return [dict(w) for _,w in pd.read_csv(content, encoding='utf-8').astype(
            object).replace({np.nan: None}).iterrows()]
    elif (filename).endswith('.xlsx') or (filename).endswith('.xls'):
        return [dict(row) for _,row in pd.read_excel(content).astype(
            object).replace({np.nan: None}).iterrows()]
    elif (filename).endswith('.json'):
        return [dict(w) for _,w in pd.read_json(content).astype(
            object).replace({np.nan: None}).iterrows()]
    else:
        raise ValueError('Unsupported file extension')


def process_data(data: List):
    for project in data:
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
                if isinstance(i[key], str):
                    if not f'Распределение по {key}' in final_report_dict.keys():
                                        final_report_dict[f'Распределение по {key}'] = {}
                    if not i[key] in final_report_dict[f'Распределение по {key}'].keys():
                        final_report_dict[f'Распределение по {key}'].setdefault(i[key], 1)
                    else:
                        final_report_dict[f'Распределение по {key}'][i[key]] +=1
                    final_report_dict[f'Распределение по {key}'] = dict(sorted(final_report_dict[f'Распределение по {key}'].items(), key=lambda x: x[1], reverse=True))
                elif isinstance(i[key], list):
                    for value in i[key]:
                        if isinstance(value, dict):
                            if not 'Распределение по странам' in final_report_dict.keys():
                                final_report_dict['Распределение по странам'] = {}
                            if not list(value.keys())[0] in final_report_dict['Распределение по странам'].keys():
                                final_report_dict['Распределение по странам'].setdefault(list(value.keys())[0], 1)
                            else:
                                final_report_dict['Распределение по странам'][list(value.keys())[0]] +=1
                        elif isinstance(value, str):
                            if not f'Распределение по {key}' in final_report_dict.keys():
                                final_report_dict[f'Распределение по {key}'] = {}
                            if not value in final_report_dict[f'Распределение по {key}'].keys():
                                final_report_dict[f'Распределение по {key}'].setdefault(value, 1)
                            else:
                                final_report_dict[f'Распределение по {key}'][value] +=1
                            final_report_dict[f'Распределение по {key}'] = dict(sorted(final_report_dict[f'Распределение по {key}'].items(), key=lambda x: x[1], reverse=True))
    return final_report_dict


def vector_serch(emb_query, search_limit:int, db):
    vector_req = (
        select(Models.Project).join(Models.Project.key_facts_relation)
        .options( 
            joinedload(Models.Project.key_facts_relation)
        ).order_by(Models.Key_fact.embedding.cosine_distance(emb_query)).limit(search_limit)
    )
            # vec_response = [
            #     {
            #         'project_name': i.name,
            #         'content': j.text,
            #         'embedding': j.embedding
            #     }  for i in db.execute(vector_req).scalars().unique().all() for j in i.key_facts_relation
            # ]
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


def rerank(query, candidates, top_n:int):
    scores = reranker.predict([(query, c[1]) for c in candidates])
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    # return [c for c, _ in ranked[:top_n]]
    return [UUID(c[0]) for c, _ in ranked[:top_n]]               
