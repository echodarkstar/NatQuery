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


nlp = spacy.load('en')

db_infodict = db_info()
print_dict(db_infodict, len(db_infodict.keys()))
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

'''
Spacy dependency parsing
Input: str
Output: PrettyTable
'''
def parse_dependency(text):
    t = PrettyTable(['Text','Lemma','POS','Tag','Dep','Shape','alpha','stop'])
    doc = nlp(text)
    print("")
    # noun_list = []
    # adj_list = []
    # verb_list = []
    ner_list = []
    # modifiers = []
    tables = []
    columns = []
    values = []
    agg = []

    is_noun = lambda pos: pos[:2] == 'NN'
    is_mod = lambda pos: pos[-3:] == 'mod'
    nl_infodict = {}
    for token in doc:
        #nl_infodict['token_info'][str(token)] = [token.text, token.lemma_, token.pos_, token.tag_, token.dep_, [child for child in token.children]]
        token_list = [token.text, token.lemma_, token.pos_, token.tag_, token.dep_, [child for child in token.children]]
        print(token_list)
        token_lemma = nlp(token.lemma_)
        #print(token.text, token.is_stop)
        if is_noun(token.tag_):
            for dbtok in db_tokens:
                if token_lemma.similarity(dbtok) == 1.0:
                    tables.append(dbtok) 
                # print(token.lemma_, dbtok.text, type(token_lemma.similarity(dbtok)))
    print(tables)
        # if is_mod(token_list[4]):
        #     modifiers.append(token_list)
        # if is_noun(token_list[3]):
        #     noun_list.append(token_list) 
        # elif 'ADJ' in token_list:
        #     adj_list.append(token_list)
        # elif 'VERB' in token_list:
        #     verb_list.append(token_list)
        # else:
        #     print(token_list)
        #t.add_row([token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop])
    for ent in doc.ents:
        ner_list.append([ent.text, ent.label_])

    # nl_infodict['noun'] = noun_list
    # nl_infodict['verb'] = verb_list
    # nl_infodict['adj'] = adj_list
    # nl_infodict['ner'] = ner_list
    # nl_infodict['modifiers'] = modifiers
    #displacy.render(doc, style='dep')
    query_info = {}
    query_info["tables"] = tables
    # query_info["columns"] = 
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

def db_element_selector(query_info):
    print("-"*100 )
    tables = query_info["tables"]
    if len(tables) ==1:
        table_name = str(tables[0])
        columns = ['title', 'rating']
        result = db.session.query(class_mapping[table_name]).options(load_only(*columns))        
        generate_query(result)
        #return result
        # for x in result:
        #     my_attrs = attrgetter('title', 'rating')(x)
        #     # fcall = getattr(x, 'title')
        #     print(my_attrs)
        #     print("")
    else:
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