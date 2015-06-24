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

def make_xml_text_code(text):
    lines_old =  text.splitlines()
    lj=None
    lines = []
    for line in lines_old:
        if line.strip() == '':
            continue
        if lj is None:
            line_lj = line.lstrip(' ')
            lj = len(line) - len(line_lj) 
        code=line[lj:]
        lines.append(code + '\n')
    return '\n'.join(lines)

def cast_expr(value, *args, **kwargs):
    namespace = {}
    value=r'%s' % value
    value=value.replace('\\n', '\n')
    code=compile(value, '<string>', 'exec')
    exec(code, {}, namespace)
    result=namespace['result']
    return result

def cast_eval(value, *args, **kwargs):
    result=eval(value)
    return result

castly={'integer':cast_integer,
        'float':cast_float,
        'decimal':cast_decimal,
        'string':cast_string,
        'boolean':cast_boolean,
        'list':cast_list,
        'object':cast_object,
        'datetime':cast_datetime,
        'path':cast_path,
        'expr':cast_expr,
        'eval':cast_eval,}

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
