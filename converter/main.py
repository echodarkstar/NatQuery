import time

import converter.timing
import argparse
import sys
import itertools
import spacy
from prettytable import PrettyTable
from converter.utils import get_json_content,print_dict,db_info
from app.app import app,db
from app.models import *
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import load_only
from spacy import displacy
from operator import attrgetter
from sqlalchemy.inspection import inspect
from nltk.corpus import wordnet
from itertools import product
nlp = spacy.load('en')
import math

db_infodict = db_info()
print_dict(db_infodict, len(db_infodict.keys()))
tables_list = set(db_infodict.keys())
#MAKE DB_TOKENS INTO SET FOR BETTER PERFORMANCE
db_tokens = set()
for token1 in db_infodict.keys():
    db_tokens.add(nlp(token1))

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

is_similar = lambda w1, w2: w1[:3] == w2[:3]

def nounify(verb_word):
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


'''
Spacy dependency parsing
Input: str
Output: PrettyTable
'''
def parse_dependency(text):
    # t = PrettyTable(['Text','Lemma','POS','Tag','Dep','Shape','alpha','stop'])
    doc = nlp(text)
    print("")
    ner_list = []
    tables = []
    columns = []
    values = []
    agg = []
    schema = {}

    is_noun = lambda pos: pos[:2] == 'NN'
    is_verb = lambda pos: pos[:2] == 'VB'
    is_proper = lambda pos: pos[:3] == 'NNP'
    is_mod = lambda pos: pos[-3:] == 'mod'

    is_subj = lambda pos: pos == 'nsubj'
    n_subj = []
    nl_infodict = {}
    # print("SYNONYMS")
    # print(word_similarity("location", "store"))
    # for chunk in doc.noun_chunks:
    #     print(chunk.text)
    for token in doc:
        token_list = [token.text, token.lemma_, token.pos_, token.tag_, token.dep_, [child for child in token.children]]
        print(token_list)
        token_lemma = nlp(token.lemma_)

        if is_subj(token.dep_):
            n_subj.append(token.lemma_)
        if is_noun(token.tag_) and not is_proper(token.tag_):
            if token.lemma_ in tables_list: #If non proper noun is there in table set
                tables.append(token.lemma_)
            else:                         #Else find synonyms and check those in table set
                for syn in wordnet.synsets(str(token)):
                    for l in syn.lemmas():
                        if l.name() in tables_list: 
                            tables.append(l.name())
        elif is_verb(token.tag_):
            modified_verb = nounify(token.lemma_)
            flag = [token.lemma_ for w2 in tables_list if is_similar(token.lemma_,w2)]
            # print("VERBLIST---- ", flag)
            if modified_verb in tables_list and len(flag)>0:
                tables.append(modified_verb)
            # print(modified_verb)

    # print(tables)
    for ent in doc.ents:
        ner_list.append([ent.text, ent.label_])
    # print("NER " ,ner_list)
    for tab in tables:
        for tok in n_subj:
            print(tok)
            columns = [x for x in db_infodict[tab] if tok in x]
            schema[tab] = columns
            # if any(tok in sl for sl in db_infodict[tab]):
            # print("COLUMN CANDIDATE- ",columns)

    query_info = {}
    query_info["tables"] = tables
    query_info["columns"] = columns
    query_info["schema"] = schema
    return (query_info)

def result_formatter(result, columns):
    for x in result:
        my_attrs = attrgetter(*columns)(x)
        yield (my_attrs)

#start_time = time.clock()
#print("Elapsed time - ", time.clock() - start_time, "seconds")

#Handling values--> 
#if current token is mapped to table/column --> add next n tokens to value list?

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}

def db_element_selector(query_info):
    print("-"*100 )
    tables = query_info["tables"]
    columns = query_info["columns"]
    
        # columns = [item for sublist in db_infodict.values() for item in sublist]
    schema = query_info["schema"]
    # print(schema)
    if len(columns) != 0:
        obj_col_list = [getattr(class_mapping[str(tab)], x) for tab,col in schema.items() for x in col ]
    else:
        for tab in tables:
            schema[tab] = db_infodict[tab]
        obj_col_list = [getattr(class_mapping[str(tab)], x) for tab,col in schema.items() for x in col ]
    print(obj_col_list)
    if len(tables) ==1:
        table_name = str(tables[0])
        columns = db_infodict[table_name]
        result = (db.session
                    .query(class_mapping[table_name])
                    .with_entities(*obj_col_list))     
        generate_query(result)
        # for x in result_formatter(result, columns):
        #     print(x)
        #return result
    else:
        # columns = ['Film.title', 'Actor.first_name', 'Actor.last_name']

        table1 = class_mapping[str(tables[0])]
        table2 = class_mapping[str(tables[1])]

        t1_pid = (inspect(table1).primary_key[0].name)
        t2_pid = (inspect(table2).primary_key[0].name)   
        pid_list = [t1_pid,t2_pid]  

        common1 = list(set(db_infodict[tables[0]]).intersection(db_infodict[tables[1]]))

        #If the two tables have no col in common, then there exists a relationship table between them
        if len(common1) == 1:   
            pivot = ""
            for tbl, col in db_infodict.items():
                if set(pid_list).issubset(set(col)):
                    pivot = class_mapping[str(tbl)]
            result = (db.session
                .query(pivot, table1, table2)
                    .join(table1)
                    .join(table2)    
                # .filter(Actor.actor_id == FilmActor.actor_id)
                # .filter(Film.film_id == FilmActor.film_id)
                .with_entities(*obj_col_list))
        else:
            result = (db.session
                .query(table1)
                    .join(table2)
                    .with_entities(*obj_col_list))
                # .filter(Actor.actor_id == FilmActor.actor_id)
                # .filter(Film.film_id == FilmActor.film_id)
                # .with_entities(Actor.first_name, Actor.last_name, Film.title))

            # .options(load_only(*columns)))
        # print(result.all())
        # for x in result:
        #     x_dict = []
        #     for y in x:
        #         x_dict.append(object_as_dict(y))
        #     print(x_dict)
        #     print("---------")
        # for x in result_formatter(result, ['title', 'rating']):
        #     print(x)

        # print(result_formatter(result, ['actor.actor_id', 'film.film_id', 'actor.first_name', 'film.title']))

        # else:
        #     result = (db.session
        #         .query(pivot, table1, table2)
                # .join(table1)
                # .join(table2))    
        generate_query(result)
        # print("More than 1 table")

def generate_query(query_obj):
    # q = db.session.query(sketch['table'])
    a = (str(query_obj.statement.compile(dialect=postgresql.dialect())))
    print(a)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Enter natural language')
    parser.add_argument('query', type=str,
                        help='Enter natural lang query')

    args = parser.parse_args()

    query_info = parse_dependency(args.query)

    print(db_element_selector(query_info))