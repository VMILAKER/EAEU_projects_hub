import logging
from typing import List

from sqlalchemy import or_
import pandas as pd
import numpy as np

import src.models as Models

logging.getLogger().setLevel(logging.INFO)


def build_filter(filter_dict: dict) -> List:
    """The filter for dynamic search throughout database

    Args:
        filter_dict (dict): The dictationary of dynamic filters

    Returns:
        List: List of filters for the request
    """
    filters = []
    for key, value in filter_dict.items():
        if value:
            if isinstance(filter_dict[key], list):
                if key in ['theme', 'supervisor']:
                    filter_theme = []
                    filter_superv = []
                    for item in filter_dict[key]:
                        if key == 'theme':
                            filter_theme.append(
                                (Models.GQW_model.theme.icontains(item)))
                        if key == 'supervisor':
                            filter_superv.append(
                                getattr(Models.GQW_supervisor, 'name') == item)
                    filters.append(or_(*filter_theme))
                    filters.append(or_(*filter_superv))
                else:
                    filters.append(
                        getattr(Models.GQW_model, key).in_(filter_dict[key]))
            else:
                if key == 'type_of_qualification':
                    filters.append(
                        getattr(Models.GQW_qualification, 'qualification') == value)
                else:
                    filters.append(getattr(Models.GQW_model, key) == value)
    return filters


def load_df(filename, content):
    if (filename).endswith('.csv'):
        return pd.read_csv(content, encoding='utf-8').astype(
            object).replace({np.nan: None})
    elif (filename).endswith('.xlsx') or (filename).endswith('.xls'):
        return pd.read_excel(content).astype(
            object).replace({np.nan: None})
    elif (filename).endswith('.json'):
        return pd.read_json(content).astype(
            object).replace({np.nan: None})
    else:
        raise ValueError('Unsupported file extension')
