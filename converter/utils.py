import json
from app.app import app,db

'''
Get json content as dictionary
Input: file_name
Output: dict
'''
def get_json_content(file_name):
    with open(file_name) as handle:
        op_dict = json.loads(handle.read())
    return (op_dict)

'''
Write dictionary to json file
Input:  new_dict
        file_name
Output: No return value
'''
def write_dict_json(new_dict, file_name):
    with open(file_name, 'w') as fp:
        json.dump(new_dict, fp)

'''
Get database info
Input:  no input
Output: dict (table:columns)
'''
def db_info():
    db_tables = (db.engine.table_names())
    mapping = {}
    for table in db_tables:
        mapping[table] = [x[0] for x in db.engine.execute("select column_name from information_schema.columns where table_name = '" + table + "'")]
    return (mapping)

'''
Neatly display dictionaries
Input:  dict
        n (no. of key value pairs to print)
Output: Returns nothing, prints prettified input dict
'''
def print_dict(ip_dict, n):
    for key in list(ip_dict.keys())[:n]:
        print(key, " -- ", ip_dict[key])

if __name__ == '__main__':
    from moz_sql_parser import parse
    import json
    print_dict(db_info(), len(db_info().keys()))
    print("-"*50)
    print((parse("select distinct course_name from courses,teach,professor where professor_name ='Smith' and prof_id = prof_teach_id and course_teach_id = course_id")))
    print(parse("SELECT ID FROM Orders WHERE Date BETWEEN ‘01/12/2018’ AND ‘01/13/2018’"))
    #write_dict_json(db_info(), 'pagila_db.json')