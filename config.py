import os

from dotenv import load_dotenv

load_dotenv()


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

        return f'postgresql+psycopg2://{user}:{password}@{server}:{port}/{name}'


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
