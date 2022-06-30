from typing import Dict

from django import template
from lis.models import NormalRange

register = template.Library()

@register.simple_tag(takes_context=True)
def get_dict_elt(context, dict:Dict, key:str):
    # a template tag that will return str representation of normal range
    try:
        nrange:NormalRange = dict.get(key, None)
        if nrange:
            return f' {nrange.min_value} - {nrange.max_value}  {nrange.m_unit}'
        return 'not available'
    except: 
        return ''