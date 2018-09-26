import converter.timing
import argparse
from nltk import sent_tokenize, word_tokenize, pos_tag
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

db_infodict = db_info()
# print_dict(db_infodict, len(db_infodict.keys()))
tables_list = db_infodict.keys()
#MAKE DB_TOKENS INTO SET FOR BETTER PERFORMANCE
db_tokens = []
for token1 in db_infodict.keys():
    db_tokens.append(nlp(token1))

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
'''
Get pos tag info from text
Input: str
Output: list (nouns), list (verbs)
'''
def get_pos_tags(text):
    # text = preprocess(text)
    is_noun = lambda pos: pos[:2] == 'NN'
    is_verb = lambda pos: pos[:2] == 'VB'

    pos_tags = [pos_tag(word_tokenize(sent)) for sent in sent_tokenize(text)]
    pos_tags = list(itertools.chain.from_iterable(pos_tags))
    print(pos_tags)
    nouns = [word for (word, pos) in pos_tags if is_noun(pos)] 
    # nouns = [noun for noun in nouns if noun.lower() not in stopwords]
    verbs = [word for (word, pos) in pos_tags if is_verb(pos)] 

    return list(set(nouns)), verbs

def nounify(verb_word):
    # set_of_related_nouns = set()
    for lemma in wordnet.lemmas(wordnet.morphy(verb_word, wordnet.VERB), pos="v"):
        for related_form in lemma.derivationally_related_forms():
            for synset in wordnet.synsets(related_form.name(), pos=wordnet.NOUN):
                if wordnet.synset('person.n.01') in synset.closure(lambda s:s.hypernyms()):
                    return (synset.lemmas()[0].name())
                    # for l in synset.lemmas():
                    #     set_of_related_nouns.add(l.name())
    # return set_of_related_nouns

 
'''
Spacy dependency parsing
Input: str
Output: PrettyTable
'''
def parse_dependency(text):
    t = PrettyTable(['Text','Lemma','POS','Tag','Dep','Shape','alpha','stop'])
    doc = nlp(text)
    print("")
    ner_list = []
    tables = []
    columns = []
    values = []
    agg = []

    is_noun = lambda pos: pos[:2] == 'NN'
    is_verb = lambda pos: pos[:2] == 'VB'
    is_proper = lambda pos: pos[:3] == 'NNP'
    is_mod = lambda pos: pos[-3:] == 'mod'
    nl_infodict = {}

    # allsyns1 = set(ss for word in doc for ss in wordnet.synsets(str(word)))
    # allsyns2 = set(ss for word in db_tokens for ss in wordnet.synsets(str(word)))
    # # print(allsyns1)
    # # print(allsyns2)
    # best = sorted(((wordnet.wup_similarity(s1, s2) or 0, s1, s2) for s1, s2 in 
    #         product(allsyns1, allsyns2)), reverse=True)[:5]
    # for i in best:
    #     print(i)

    # for chunk in doc.noun_chunks:
    #     print(chunk.text)
    for token in doc:
        token_list = [token.text, token.lemma_, token.pos_, token.tag_, token.dep_, [child for child in token.children]]
        print(token_list)
        token_lemma = nlp(token.lemma_)

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
            if modified_verb in tables_list:
                tables.append(modified_verb)
            print(modified_verb)

        # if is_noun(token.tag_) or is_verb(token.tag_):
        #     for dbtok in db_tokens:
        #         if token_lemma.similarity(dbtok) == 1.0:
        #             tables.append(dbtok)
        #         else:
        #             if not is_proper(token.tag_) and is_noun(token.tag_):
        #                 synonyms = []
        #                 for syn in wordnet.synsets(str(token)):
        #                     for l in syn.lemmas():
        #                         token_lemma = nlp(l.name())
        #                         # if l.name() != token.tag_:
        #                         if token_lemma.similarity(dbtok) == 1.0:
        #                             tables.append(dbtok)
        #             elif is_verb(token.tag_):
        #                 modified_verb = nounify(token.lemma_)
        #                 print(modified_verb)

                        #             synonyms.append(l.name())
                        # synonyms = set(synonyms)
                        # print("Synonyms --", synonyms)

         
                # print(token.lemma_, dbtok.text, (token_lemma.similarity(dbtok)))
    print(tables)
    for ent in doc.ents:
        ner_list.append([ent.text, ent.label_])
    query_info = {}
    query_info["tables"] = tables

    return (query_info)

# def create_sketch():
#     sketch = {
#         'select' : '',
#         'agg' : '',
#         'from' : '',
#         'where' : [{
#             'column' : '',
#             'op' : '',
#             'value' : ''
#         }]
#     }

def result_formatter(result, columns):
    for x in result:
        my_attrs = attrgetter(*columns)(x)
        return my_attrs

def db_element_selector(query_info):
    print("-"*100 )
    tables = query_info["tables"]
    if len(tables) ==1:
        table_name = str(tables[0])
        columns = db_infodict[table_name]
        result = (db.session
                    .query(class_mapping[table_name])
                    .options(load_only(*columns))  )      
        generate_query(result)
        # result_formatter(result, ['title', 'rating'])
        #return result
    else:
        table1 = class_mapping[str(tables[0])]
        table2 = class_mapping[str(tables[1])]

        t1_pid = (inspect(table1).primary_key[0].name)
        t2_pid = (inspect(table2).primary_key[0].name)     
        pid_list = [t1_pid,t2_pid]   
        pivot = ""
        for tbl, col in db_infodict.items():
            if set(pid_list).issubset(set(col)):
                pivot = class_mapping[str(tbl)]
        # tables.append(pivot)
        result = (db.session
            .query(pivot, table1, table2)
            .join(table1)
            .join(table2))      
        generate_query(result)
        print("More than 1 table")

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