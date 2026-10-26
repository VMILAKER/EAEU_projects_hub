import os

from dotenv import load_dotenv

load_dotenv()
import logging

logging.getLogger().setLevel(logging.INFO)

def get_database_url():
    empty_entities = []
    for i in ['DB_USER', 'DB_PASSWORD', 'DB_NAME', 'DB_SERVER', 'DB_PORT']:
        if not os.getenv(i):
            empty_entities.append(i)

    if empty_entities:
        raise ValueError(
            f'{','.join(empty_entities)} missed')
    else:
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        name = os.getenv('DB_NAME')
        server = os.getenv('DB_SERVER')
        port = os.getenv('DB_PORT')
        container_name = os.getenv('DB_CONTAINER_NAME')

        # return f'postgresql+psycopg2://{user}:{password}@{server}:{port}/{name}'
        return f'postgresql+psycopg2://{user}:{password}@{container_name}/{name}'


def get_sentence_transformer_model_name():
    model_name = os.getenv("SENTENCE_TRANSFORMER_MODEL_NAME")
    if model_name:
        return model_name
    else:
        raise ValueError('No name for SENTENCE_TRANSFORMER_MODEL_NAME')


def get_backend_api_key():
    if os.getenv('INTERNAL_BACKEND_API_KEY'):
        return os.getenv('INTERNAL_BACKEND_API_KEY')
    else:
        raise ValueError('INTERNAL_BACKEND_API_KEY is not provided')


def get_instruction():
    prompt = os.getenv('INSTRUCTION_PROMPT')
    if prompt:
        return prompt
    else:
        raise ValueError('No prompt provided')

    
def create_payload(query:str, text:str):
    model_name = os.getenv('LLM_NAME')
    temperature = os.getenv('LLM_TEMPERATURE')
    language = os.getenv('ANSWER_LANGUAGE')
    if model_name and temperature and language:
        if query and not text:
            return {
                    "model": model_name,
                    "messages":[{
                        "role": "user",
                        "content": f'Extract named entities from text: {query}. If it is a infrastructure (e.g. Electic Line) \
                        and some actions should be applied (e.g. to renew, to modify) from text find out materials from what object consists of. Answer in {language}. Answer shortly',
                        },],
                    "stream": False,
                    "tempetature": float(temperature)
            }
        elif query and text:
            return {
                "model": model_name,
                "messages":[{
                    "role": "user",
                    "content":  f"{get_instruction()}\n\n \
                                    Origins:{text}\n\n Question:{query}. Always reply in  {language}. Do not TOTALLY use English in your replies"
                    },],
                "stream": False,
                "tempetature": float(temperature)
            }

    else:
        raise ValueError('No LLM_NAME or LLM_TEMPERATURE, or ANSWER_LANGUAGE provided')


def get_ollama_api_url():
    ollama_port = os.getenv('OLLAMA_PORT')
    ollama_container_name = os.getenv('OLLAMA_CONTAINER_NAME')
    if ollama_port and ollama_container_name:
        return f"http://{ollama_container_name}:11434/api/chat"
    else:
        raise ValueError('No mention about OLLAMA_PORT or OLLAMA_CONTAINER_NAME')


def get_origins_request_limit():
    origins_limit = os.getenv('ORIGINS_LIMIT')
    if origins_limit:
        return origins_limit
    else:
        raise ValueError('ORIGINS_LIMIT is not provided')


def get_cross_encoder_name():
    cross_encoder = os.getenv('CROSS_ENCODER')
    if cross_encoder:
        return cross_encoder
    else:
        raise ValueError('CROSS_ENCODER is not provided')


def get_statistics_key_template(key):
    return f'Распределение по {key}'

def get_statistics_form_template(report_dict:dict, key_template: str, value):
    if not key_template in report_dict:
        report_dict[key_template] = {}
    if not value in report_dict[key_template].keys():
        report_dict[key_template].setdefault(value, 1)
    else:
        report_dict[key_template][value] +=1
    report_dict[key_template] = dict(sorted(report_dict[key_template].items(), key=lambda x: x[1], reverse=True))
    return report_dict

    
def get_frontend_url():
    frontend_url_internal = os.getenv('INTERNAL_FRONTEND_URL')
    frontend_url_external = os.getenv('EXTERNAL_FRONTEND_URL')
    frontend_port = os.getenv('FRONTEND_PORT')
    if frontend_url_internal and frontend_port and frontend_url_external:
        return [frontend_url_internal, frontend_url_external, f'172.7.0.1:{frontend_port}', f"http://0.0.0.0:{frontend_port}",f"http://localhost:{frontend_port}"]
    else:
        ValueError('frontend_urls or PORT are missing')


def get_secret_word():
    secret_word = os.getenv('SECRET_WORD')
    if secret_word:
        return secret_word
    else:
        ValueError('SECRET_WORD missing')

