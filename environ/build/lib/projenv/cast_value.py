'''
Created on Mar 16, 2015

@author: arnon
'''

from datetime import datetime
import dateutil
import json
from decimal import Decimal
import ast
from symbol import except_clause
import logging

class CastError(Exception):
    pass

logger=logging.getLogger(__name__)

def cast_decimal(name, value, *args, **kwargs):
    try:
        result=Decimal(value)
    except Exception as e:
        message = "Failed Decimal {} cast: {}: {}".format(name, value, repr(e))
        logger.error(message)
        raise CastError(message)
    return result

def cast_string(name, value, *args, **kwargs):
    try:
        result=str(value)
    except Exception as e:
        message = "Failed str {} cast: {}: {}".format(name, value, repr(e))
        logger.error(message)
        raise CastError(message)
    return result

def cast_object(name, value, *args, **kwargs):
    return value

def cast_path(name, value, *args, **kwargs):
    parts=value.split('\\')
    return '/'.join(parts)

def cast_datetime(name, value, fmt=None, *args, **kwargs):
    try:
        if fmt:
            return datetime.strptime(value, fmt)
        else:
            return dateutil.parser.parse(value)
    except Exception as e:
        message = "Failed datetime {} cast: {}: {}".format(name, value, repr(e))
        logger.error(message)
        raise CastError(message)

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

def cast_expr(name, value, *args, **kwargs):
    namespace = {}
    value=r'%s' % value
    value=value.replace('\\n', '\n')
    try:
        code=compile(value, '<string>', 'exec')
    except Exception as e:
        message = "Failed compiling expression {} cast: {}: {}".format(name, value, repr(e))
        logger.error(message)
        raise CastError(message)
    
    try:
        exec(code, {}, namespace)
    except Exception as e:
        message="Failed exec expression cast {} value: {}: {}".format(name, value, repr(e))
        logger.error(message)
        raise CastError(message)
    
    result=namespace['result']
    return result

def cast_literal(name, value, *args, **kwargs):
    try:
        result=ast.literal_eval(value)
    except Exception as e:
        raise CastError('Failed literal cast {} value: {}; {}'.format(name, value, repr(e)))
    return result

def cast_eval(name, value, *args, **kwargs):
    try:
        result=eval(value)
    except Exception as e:
        raise CastError('Failed eval cast {} value: {}; {}'.format(name, value, repr(e)))
    return result

castly={'integer':cast_literal, #cast_integer,
        'float':cast_literal, #cast_float,
        'decimal':cast_decimal,
        'string':cast_string,
        'boolean':cast_literal, #cast_boolean,
        'list':cast_literal, #cast_list,
        'object':cast_object,
        'datetime':cast_datetime,
        'path':cast_path,
        'literal':cast_literal,
        'expr':cast_expr,
        'eval':cast_eval,}

def cast_value(name, target_type, value=None, attrib={},logclass=None):
    if logclass:
            global logger
            logger=logging.getLogger('.'.join([logclass, "cast_value"]))
    try:
        cast=castly[target_type]
    except KeyError:
        raise CastError('Unknown type: {}'.format(target_type))
    if value is not None:
        return cast(name=name, value=value, **attrib)
    else:
        if 'name' in list(attrib.keys()):
            return cast(**attrib)
        else:
            return cast(name=name, **attrib)
