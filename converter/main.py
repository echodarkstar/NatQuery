import argparse
from nltk import sent_tokenize, word_tokenize, pos_tag
import itertools
import spacy
from prettytable import PrettyTable


def get_pos_tags(text):
    # text = preprocess(text)
    is_noun = lambda pos: pos[:2] == 'NN'
    is_verb = lambda pos: pos[:2] == 'VB'

    pos_tags = [pos_tag(word_tokenize(sent)) for sent in sent_tokenize(text)]
    pos_tags = list(itertools.chain.from_iterable(pos_tags))
    print(pos_tags)
    # print()
    # print(pos_tags)
    # print()    
    nouns = [word for (word, pos) in pos_tags if is_noun(pos)] 
    # nouns = [noun for noun in nouns if noun.lower() not in stopwords]
    verbs = [word for (word, pos) in pos_tags if is_verb(pos)] 

    return list(set(nouns)), verbs

def parse_dependency(text):
    t = PrettyTable(['Text','Lemma','POS','Tag','Dep','Shape','alpha','stop'])
    nlp = spacy.load('en')
    doc = nlp(text)
    print("")
    for token in doc:
        t.add_row([token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
            token.shape_, token.is_alpha, token.is_stop])
    print(t)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Enter natural language')
    parser.add_argument('query', type=str,
                        help='Enter natural lang query')

    args = parser.parse_args()

    nouns, verbs = (get_pos_tags(args.query))
    print("Nouns\t", nouns)
    print("Verbs\t", verbs)
    print("Spacy")
    parse_dependency(args.query)