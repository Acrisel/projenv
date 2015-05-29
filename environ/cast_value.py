'''
Created on Mar 16, 2015

@author: arnon
'''

from datetime import datetime
import dateutil
import json
from decimal import Decimal

def cast_integer(value, *args, **kwargs):
    return int(value)

def cast_float(value, *args, **kwargs):
    return float(value)

def cast_decimal(value, *args, **kwargs):
    return Decimal(value)

def cast_string(value, *args, **kwargs):
    return str(value)

def cast_boolean(value, *args, **kwargs):
    return json.loads(value.lower())

def cast_list(value, *args, **kwargs):
    return json.loads(value)

def cast_object(value, *args, **kwargs):
    return value

def cast_path(value, *args, **kwargs):
    parts=value.split('\\')
    return '/'.join(parts)

def cast_datetime(value, fmt=None, *args, **kwargs):
    if fmt:
        return datetime.strptime(value, fmt)
    else:
        return dateutil.parser.parse(value)

castly={'integer':cast_integer
       ,'float':cast_float
       ,'decimal':cast_decimal
       ,'string':cast_string
       ,'boolean':cast_boolean
       ,'list':cast_list
       ,'object':cast_object
       ,'datetime':cast_datetime
       ,'path':cast_path}

class CastError(Exception):
    def __init__(self, msg):
        self.msg = msg
    
    def __str__(self):
        return '{}'.format(self.msg)
        
    def __repr__(self):
        return '{}'.format(self.msg)

def cast_value(target_type, value=None, attrib={}):
    try:
        cast=castly[target_type]
    except KeyError:
        raise CastError('Unknown type: {}'.format(target_type))
    if value is not None:
        return cast(value=value, **attrib)
    else:
        return cast(**attrib)