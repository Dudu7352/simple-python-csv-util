import re
def to_snake(camel_case):
    callback = lambda pat: f'{pat.group(1)[0]}_{pat.group(1)[1]}'
    return re.sub(r'([a-z][A-Z])', callback, camel_case.replace(' ','_').replace('ID', 'id_')).lower()


print(to_snake("IDucznia"))