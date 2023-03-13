import itertools
from database import *
from shallowAnalysis import shallow_linguistic_analysis, load_model
from disambiguate import *


def translate_to_pictos(text, neural_dis, picto_table, wn_table, nlp_model):
    """
    Function that translates text into all possible translation in pictogram sequence.

    :param out_wsd: dict with the wsd sentence per utterance
    :return dict with all possible translations in picto per utterance
    """

    # generate wsd model
    sentence_proc, sentence_wsd = disambiguate(text, neural_dis)

    s = shallow_linguistic_analysis(nlp_model, text, sentence_wsd)

    # Find pictograms corresponding to each word of each sentences
    pictos_s = []
    pictos_lemma = []
    # pour chaque mot
    for w in s:
        picto_ids_from_wn = list(set(get_arasaac_picto_by_wn(wn_table, picto_table, w.wn)))
        picto_ids_from_lemma = list(set(get_araasac_picto_id_by_lemma(picto_table, w.lemma, w.pos)))
        pictos_s.append([picto_ids_from_wn, picto_ids_from_lemma])
    pictos = generate_all_translations_from_generated_pictos(pictos_s)
    for p in pictos:
        pictos_lemma.append(get_lemma_by_id_picto(picto_table, p))
    return pictos, pictos_lemma


def generate_all_translations_from_generated_pictos(pictos_s):
    """
        Function which combine the picto per word into possible translation in sequence

        :param out_wsd_pictos: dict with the wsd sentence per utterance
        :return dict with all possible translations in picto per utterance
    """
    to_keep_to_generate_translations = []  # because we don't want [[None],[None]] in our table
    for word_id in pictos_s:
        if any(elem is not None for elem in word_id[0] + word_id[1]):
            to_keep_to_generate_translations.append(word_id)
    res = list(itertools.product(*to_keep_to_generate_translations))
    result = [tuple for tuple in res if None not in sum(tuple, [])]
    all_combinations = [x for i in result for x in list(itertools.product(*i))]
    all_possible_trans = [list(a) for a in
                          all_combinations]  # récupère seulement les traductions avec les mots transcrits
    all_possible_trans = [list(i) for i in set(map(tuple, all_possible_trans))]  # to remove duplicates
    return all_possible_trans[:1][0]
