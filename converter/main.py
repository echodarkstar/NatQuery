import time

import converter.timing
import argparse
import sys
import itertools
import spacy
import random
from prettytable import PrettyTable
# from app.app import app,db
from converter.utils import get_json_content,print_dict,db_info
# from app.models import *
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import load_only
from spacy import displacy
from operator import attrgetter
from sqlalchemy.inspection import inspect
from nltk.corpus import wordnet
from itertools import product
nlp = spacy.load('en')
import math
from sqlalchemy import func


# type_mapping = {
#     Integer() : "INT",
#     Text() : "STRING",
#     # class 'sqlalchemy.sql.sqltypes.ARRAY' : "Array"
# }
is_similar = lambda w1, w2: w1[:3] == w2[:3]

def nounify(verb_word, tables_list):
    # set_of_related_nouns = set()
    for lemma in wordnet.lemmas(wordnet.morphy(verb_word, wordnet.VERB), pos="v"):
        for related_form in lemma.derivationally_related_forms():
            for synset in wordnet.synsets(related_form.name(), pos=wordnet.NOUN):
                # print(synset, "-------" ,get_hypernyms(synset))
                # for syn in synset.closure(lambda s:s.hypernyms()):
                #     print (syn)
                
                if wordnet.synset('physical_entity.n.01') in synset.closure(lambda s:s.hypernyms()):
                    result = [x.name() for x in synset.lemmas() if x.name() in tables_list]
                    # print(result)
                    if len(result)!=0:
                        return result[0]
                        
                    # for l in synset.lemmas():
                    #     set_of_related_nouns.add(l.name())
    # return set_of_related_nouns

def join_nouns(token_list, values, used_nouns):
    

    for x in token_list[-1]:
        # print(x)
        if x.text in values:
            # print(x.text)
            used_nouns.append(x.text)
            values.remove(x.text)
            values.append(x.text + " " + token_list[0])
            # print("inn - ", values)
            return values, used_nouns
        else:
            pass
    return values, used_nouns

flatten = lambda l: [item for sublist in l for item in sublist]

'''
Spacy dependency parsing
Input: str
Output: PrettyTable
'''
def parse_dependency(text, db, class_mapping):
    db_infodict = db_info(db)
    # print_dict(db_infodict, len(db_infodict.keys()))
    tables_list = set(db_infodict.keys())
    columns_list = set(flatten(db_infodict.values()))
    # print(columns_list)
    # t = PrettyTable(['Text','Lemma','POS','Tag','Dep','Shape','alpha','stop'])
    doc = nlp(text)
    # print("")
    ner_list = []
    tables = []
    columns = set()
    values = []
    #Use pobj and dobj for column names and check if they are valid col names. Also make sure it is not a table
    agg = []               
    schema = {}
    # extra_cols = []
    is_noun = lambda pos: pos[:2] == 'NN'
    is_verb = lambda pos: pos[:2] == 'VB'
    is_proper = lambda pos: pos[:3] == 'NNP'
    is_mod = lambda pos: pos[-3:] == 'mod'
    is_wq = lambda pos: pos[0] == 'W'
    is_subj = lambda pos: pos == 'nsubj'
    is_obj = lambda pos: pos[-3:] == 'obj'
    n_subj = []
    n_obj = []
    nl_infodict = {}
    # print("SYNONYMS")
    # print(word_similarity("location", "store"))
    # for chunk in doc.noun_chunks:
    #     print(chunk.text)
    used_nouns = []
    total_used = []
    used_word_index = 0
    text_list = text.split()
    last_index = 0
    for index,token in enumerate(doc):
        token_list = [token.text, token.lemma_, token.pos_, token.tag_, token.dep_, [child for child in token.children]]
        print(token_list)
        token_lemma = nlp(token.lemma_)
        try:
            if is_wq(token.tag_):
                used_nouns.append(token.lemma_)
        except:
            pass
        if is_subj(token.dep_):
            n_subj.append(token.lemma_)
        # print(n_subj)
        if is_obj(token.dep_):
            n_obj.append(token.lemma_)
        if is_noun(token.tag_) and not is_proper(token.tag_):
            if token.lemma_ in tables_list: #If non proper noun is there in table set
                tables.append(token.lemma_)
                used_nouns.append(token.lemma_)
                used_word_index = index
                # values += [x for x in text_list[index+1:] if is_noun(x) and x not in tables_list]
            else:
                syn_flag = False                         #Else find synonyms and check those in table set
                for syn in wordnet.synsets(str(token)):
                    for l in syn.lemmas():
                        if l.name() in tables_list:
                            syn_flag = True 
                            tables.append(l.name())
                            used_nouns.append(token.lemma_)
                            used_word_index = index
                            break     
                if not syn_flag:
                    if len(token_list[-1]) != 0:
                        # values += ([x.text + " " + token.text for x in token_list[-1] if x.text in values])
                        # values.remove('b')
                        # print(used_nouns)
                        values, used_nouns = (join_nouns(token_list, values, used_nouns))
                    else:
                        values.append(token.text)    
        elif is_verb(token.tag_):
            try:
                modified_verb = nounify(token.lemma_, tables_list)
                flag = [token.lemma_ for w2 in tables_list if is_similar(token.lemma_,w2)]
                # print("VERBLIST---- ", flag)
                if modified_verb in tables_list and len(flag)>0:
                    tables.append(modified_verb)
                    total_used.append(token.text)
            except Exception as e:
                print("Nounify - ", e)
        if is_proper(token.tag_):
            # print(values)
            if len(token_list[-1]) != 0:
                # values += ([x.text + " " + token.text for x in token_list[-1] if x.text in values])
                # values.remove('b')
                # print(used_nouns)
                values, used_nouns = (join_nouns(token_list, values, used_nouns))
            else:
                values.append(token.text)   
            # values.append(token.text)

        last_index += 1
            # print(modified_verb)
    for ent in doc.ents:
        ner_list.append([ent.text, ent.label_])
    # print("NER " ,ner_list)
    if len(ner_list) !=0:
        for x in ner_list:
            if not any(x[0] in val for val in values):
                # print(x[1])
                if x[1] == 'DATE' or x[1] == 'CARDINAL':
                    print(x[0], " " ,x[1])
                    values.append(int(float(x[0])))
                else:
                    values.append(x[0])
    if token.text[0] == 'W':
        for tab in tables:
            for tok in n_subj:
                print("AAA " ,tok, tab,  db_infodict[tab])
                for x in db_infodict[tab]:
                    if tok in x:
                        columns.add(x)
                        schema[tab] = columns
    else:
        for tab in tables:
            for tok in n_obj:
                print("AAA " ,tok, tab,  db_infodict[tab])
                for x in db_infodict[tab]:
                    if tok in x:
                        columns.add(x)
                        schema[tab] = columns

        # for tok in n_obj:
        #     for x in db_infodict[tab]:
        #         if tok in x:
        #             columns.add(x)
        #             schema[tab] = columns

    #DO ANOTHER CHECK. SEE IF ANYTHING IN VALUES AND COLUMNS IS COMMON. REMOVE THE COMMON ELEMENT.
    try:
        values = [i for i in values if i not in columns]
    except:
        pass
    # print("VAL ", values)
    query_info = {}
    query_info["tables"] = tables
    query_info["columns"] = list(columns)
    query_info["schema"] = schema
    query_info["values"] = values
    total_used = total_used + used_nouns + values + list(columns)
    query_info["interpreted_words"] = list(set(total_used))
    query_info["text"] = text
    # print("Used nouns", used_nouns)
    # print("VALUES - ", values)
    print_dict(query_info, len(query_info.keys()))
    return (query_info)

def result_formatter(result, columns):
    for x in result:
        my_attrs = attrgetter(*columns)(x)
        yield (my_attrs)

#start_time = time.clock()
#print("Elapsed time - ", time.clock() - start_time, "seconds")

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}

#PROBLEM QUERY - Display rentals of film (Case : rental and film have no common )
#give me the district with the postal code of 400094 address

def get_columns_by_type(schema, class_mapping):
    type_map = {x:str(getattr(class_mapping[str(tab)], x).type) for tab,col in schema.items() for x in col }
    return type_map

def db_element_selector(query_info, db, class_mapping):
    try:
        db_infodict = db_info(db)
        # print_dict(db_infodict, len(db_infodict.keys()))
        tables_list = set(db_infodict.keys())
        
        print("-"*100 )
        tables = query_info["tables"]
        columns = query_info["columns"]
            # columns = [item for sublist in db_infodict.values() for item in sublist]
        schema = query_info["schema"]
        values = query_info["values"]

    # print(schema)

        
        # print("COLS -",columns)
        # print("TAB ",tables)
        print("TYPE DICT - ", get_columns_by_type(schema, class_mapping))

        if len(columns) != 0:
            # print("SCH ", schema)
            obj_col_list = [getattr(class_mapping[str(tab)], x) for tab,col in schema.items() for x in col ]
        else:
            for tab in tables:
                schema[tab] = db_infodict[tab]
            obj_col_list = [getattr(class_mapping[str(tab)], x) for tab,col in schema.items() for x in col ]

        related = []
        for tab in schema.keys():
            for col in schema[tab]:
                related.append("Give me every " + col + " of " + tab)


        for tab in schema.keys():
            for col in schema[tab]:
                related.append("Show me every " + tab + "\'s " + col)


        for tab in schema.keys():
            for col in schema[tab]:
                related.append("What is the " + col + " of " + tab)

        final = []

        final.append(random.choice(related))
        final.append(random.choice(related))
        final.append(random.choice(related))

        # print(final)

        type_dict = get_columns_by_type(schema, class_mapping)
        print("TYPE -", type_dict)

        candidate_value_checks = []
        for val in values:
            flag = 'int'
            try:
                if int(val):
                    flag = 'int'
            except:
                flag = 'string'
            for tab,col in schema.items():
                if flag == 'int':
                    candidate_value_checks = [x for x in col if type_dict[x] == 'INTEGER' or 'SMALLINT']
                else:
                    candidate_value_checks = [x for x in col if type_dict[x] !='INTEGER' and 'SMALLINT' and 'TSVECTOR']

        print("CAND " ,candidate_value_checks)

        # print(type("PO"))
        #Only one table is selected
        if len(tables) ==1:
            table_name = str(tables[0])
            columns = db_infodict[table_name]
            try:
                # if 
                value_list = [func.lower(getattr(class_mapping[table_name], candidate_value_checks[0])) == func.lower(values[0])]
            except:
                value_list = []
            result = (db.session
                        .query(class_mapping[table_name])
                        .filter(*value_list)
                        .with_entities(*obj_col_list))     
            # print(result.all())
            # for x in result_formatter(result, columns):
            #     print(x)
            #return result
            
        #Multiple tables are selected
        else:
            # columns = ['Film.title', 'Actor.first_name', 'Actor.last_name']

            #Get table names
            table1 = class_mapping[str(tables[0])]
            table2 = class_mapping[str(tables[1])]

            #Get primary keys
            t1_pid = (inspect(table1).primary_key[0].name)
            t2_pid = (inspect(table2).primary_key[0].name)   
            pid_list = [t1_pid,t2_pid]  
            pid_map = {t1_pid:tables[0], t2_pid:tables[1]}
            #Check if two tables have any common element
            common1 = list(set(db_infodict[tables[0]]).intersection(db_infodict[tables[1]]))
            print("COMMON - ",common1)
            print_dict(query_info, len(query_info.keys()))
            #If the two tables have no col in common, then there may exist a relationship table between them
            if len(common1) == 0:   
                # print("AAAA")
                pivot = ""
                # print("PID ",pid_list)
                #non empty pivot means there's a relationship table
                for tbl, col in db_infodict.items():
                    if set(pid_list).issubset(set(col)):
                        # print("PIVOT - ", str(tbl))
                        pivot = class_mapping[str(tbl)]
                
                if pivot == "":
                    temp_schema = {tab:x for tab,col in schema.items() for x in col if x not in pid_list}
                    temp_list = [x for tab,col in schema.items() for x in col if x not in pid_list]
                    # print("Schema - ", temp_list)                
                    # print("Temp - ", temp_schema)
                    #In this case the pivot is not found. So, there must be a third table that will relate the two tables together. (not relationship table)
                    #Cross check if any (primary key, non pk of other table) exists in a table other than pk table. If so, it is the pivot 
                    for pid in pid_list:
                        for extra_col in temp_list:
                            for tbl,col in db_infodict.items():
                                if pid in col and extra_col in col:
                                    if not set([pid, extra_col]).issubset(db_infodict[pid_map[pid]]):
                                        # print([pid,extra_col])       
                                        pivot = class_mapping[str(tbl)]
                    # print("PV ", pivot)
                    # for val in values:
                #UPDATE SCHEMA ACC TO PIVOT
                # candidate_value_checks = []
                # for val in values:
                #     flag = 'int'
                #     try:
                #         if int(val):
                #             flag = 'int'
                #     except:
                #         flag = 'string'
                #     for tab,col in schema.items():
                #         if flag == 'int':
                #             candidate_value_checks = [x for x in col if type_dict[x] == 'INTEGER' or 'SMALLINT']
                #         else:
                #             candidate_value_checks = [x for x in col if type_dict[x] !='INTEGER' and 'SMALLINT']
                # print("CAND " ,candidate_value_checks)
                try:
                    value_list = [getattr(class_mapping[table_name], candidate_value_checks[0]) == (values[0])]
                except:
                    value_list = []      
                result = (db.session
                    .query(pivot, table1, table2)
                        .join(table1)
                        .join(table2)
                        .filter(*value_list).distinct()                        
                    .with_entities(*obj_col_list))
            #There is a common column between the tables on which JOIN must be performed.
            else:
                print("TYPE ",get_columns_by_type(schema, class_mapping))

                keyselect_list = [getattr(table1, common1[0]) == getattr(table2, common1[0])]
                value_list = []
                try:
                    value_list = [getattr(table1, common1[0]) == int(float(values[0]))]
                except:
                    try:
                        value_list = [getattr(table1, common1[0]) == (values[0])]
                    except:
                        value_list = []
                # print("VAL ", value_list)
                # print("SCHEMA _ ", schema)
                # for celement in common1:
                #     keyselect_list.append()
                # for tab,col in schema.items():
                #     for x in col:
                #         # mapped_col = getattr(class_mapping[str(tab)], x)
                #         col_type = get_columns_by_type(schema, class_mapping)[x]
                #         # print(mapped_col.type, type(values[0]))
                #         value_list = [mapped_col == values[0]]
                result = (db.session
                    .query(table1, table2)
                    .filter(*keyselect_list)
                    .filter(*value_list).distinct()
                        .with_entities(*obj_col_list))
        # print(result.all())
        proper_op = []
        sql_query = generate_query(result)
        vect_i = sql_query.split()
        vect_i = [x.replace(',','') for x in vect_i]
        if len(tables) !=1:
            headers = vect_i[len(vect_i) - vect_i[::-1].index('DISTINCT') : vect_i.index('FROM')] 
        else:
            headers = vect_i[len(vect_i) - vect_i[::-1].index('SELECT') : vect_i.index('FROM')] 
        # print(headers)
        for row in result.all():
            proper_op.append(dict(zip(headers, row)))
        # req_output = type(result.all())

        output_json = {
            "nl_query" : query_info["text"],
            "interpreted" : (query_info["interpreted_words"]),
            "sql_query" : sql_query,
            "output" : proper_op,
            "related_queries" : final
        }
        print(sql_query)
        return output_json
    except Exception as e:
        output_json = {
            "nl_query" : query_info["text"],
            "interpreted" : (query_info["interpreted_words"]),
            "sql_query" : [["Error interpreting"]],
            "output" : [["Error interpreting"]],
            "related_queries" : [["Error"], ["Interpreting"], ["Query"]]
        }
        print(e)
        return output_json
        print(sql_query)
        # print("More than 1 table")

def generate_query(query_obj):
    # q = db.session.query(sketch['table'])
    a = (str(query_obj.statement.compile(dialect=postgresql.dialect())))
    return (a)

if __name__ == '__main__':
    from app.models import *
    from app.app import app,db
    class_mapping = {
        "actor" : Actor,
        "film" : Film,
        "category" : Category,
        "country" : Country,
        "language" : Language,
        "city" : City,
        "address" : Addres,
        "film_actor" : FilmActor,
        "film_category" : FilmCategory,
        "store" : Store,
        "customer" : Customer,
        "inventory" : Inventory,
        "staff" : Staff,
        "rental" : Rental
    }
    parser = argparse.ArgumentParser(description='Enter natural language')
    parser.add_argument('query', type=str,
                        help='Enter natural lang query')

    args = parser.parse_args()

    query_info = parse_dependency(args.query, db,class_mapping)
    # print_dict(query_info, len(query_info.keys()))
    a = (db_element_selector(query_info, db, class_mapping))
    # print("OP - ",a)
