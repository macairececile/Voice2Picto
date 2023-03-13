import spacy
import json
import codecs
import re

from Word import Word


def load_model(model_name):
    """
    Function to load a spacy model given as input

    :param model_name: Name of the spacy model to load
    :type model_name: str
    :returns: Loaded spacy model
    :rtype: class: `spacy.lang`
    :raises Exception: if the specified model does not exist or not handled by spacy.
    """

    # Load the spacy model
    try:
        nlp = spacy.load(model_name)
        print("*** Spacy model ready to use : " + model_name + " ***")
        return nlp

    # Raise exception
    except Exception:
        print("Specified model is not installed, does not exist or is not handled by spacy !")
        print("If it exists, you may download it with : 'python -m spacy download <model_name>'.\n-> Exit")
        exit()


def shallow_linguistic_analysis(model, sentence_asr, out_wsd):
    """
    Function to apply the shallow linguistic analysis on the input text

    :param model: Spacy model
    :type model: class: `spacy.lang`
    :param input_text: Input text to apply the shallow linguistic analysis on it
    :type input_text: str
    :returns: Analyzed text
    :rtype: _
    """

    print("*** Starting the shallow linguistic analysis ***")

    # Opening JSON file containing particular Named Entities
    with codecs.open("database/namedentities.json", "r", encoding="utf8") as special_ne_f:
        special_named_entities = json.load(special_ne_f)

    sentence = []
    # Multiword Expressions Detection
    to_process = sentence_asr.replace("' ", "'")
    text = multiword_expression_detection_from_file(to_process)  # retrieve the sentence to translate
    # Tokenization, POS Tagging, Lemmatization
    doc = model(text)
    # Word informations and Sentence detection
    for token in doc:
        if token.lemma_ != " " and token.lemma_ != "'":
            # Build the word with associated informations
            w = Word(token.text, token.lemma_, token.pos_, token.ent_type_)
            check_if_mwe(w)  # check if word is a MWE - if yes put a tag
            # Particular Named Entities (medicine, etc.)
            if w.ent_type == "MISC" or w.pos == "PROPN":
                for key in special_named_entities:
                    for elem in special_named_entities[key]:
                        if (elem == w.lemma):
                            w.ent_type = key
            # Named Entity Recognition
            if w.ent_type:
                tmp = w.lemma
                w.lemma = named_entitity_substitution(w.ent_type)
                # If no substitution, keep the same word.
                if (w.lemma == ""):
                    w.lemma = tmp
                # Keeping in memory the original entity
                w.ent_text = tmp
            check_if_named_entity(w)  # check if named entity - if true, add tag
            sentence.append(w)
            # Sentence detection
            if w.pos == "PUNCT" and w.lemma in ['.', '!', '?']:
                s = add_sense_tags_to_word(out_wsd, sentence)
                s = multiword_expression_detection_from_token(s)
                return s
            # If there is no punctuation on the last sentence.
    if sentence:
        s = add_sense_tags_to_word(out_wsd, sentence)
        s = multiword_expression_detection_from_token(s)
        return s


def multiword_expression_detection_from_token(sentence):
    i = 0
    j = 0
    k = 0
    while i < len(sentence) - 3:
        if sentence[i].token == "y" and sentence[i + 1].token == "a" and sentence[i + 2].token == "t'" and sentence[
            i + 3].token == "il":
            sentence = sentence[:i] + sentence[i + 4:]
            i = 0
        elif sentence[i].token == "s'" and sentence[i + 1].token == "il" and sentence[i + 2].token in ["te", "vous"] and \
                sentence[i + 3].token in ["plaît", "plait"]:
            sentence[i:i + 4] = [Word("s'il_vous_plaît_2", "s'il_vous_plaît_2", "ADV", None, None)]
            i = 0
        elif sentence[i].token == "vous" and sentence[i + 1].token == "a" and sentence[i + 2].token == "t'" and \
                sentence[i + 3].token == "on":
            sentence[i:i + 4] = [Word("personne", "personne", "NOUN", None, None), sentence[i]]
            i = 0
        else:
            i += 1
    while j < len(sentence) - 2:
        if sentence[j].token == "est" and sentence[j + 1].token == "ce" and sentence[j + 2].token == "que":
            sentence = sentence[:j] + sentence[j + 3:]
            j = 0
        else:
            j += 1
    while k < len(sentence) - 1:
        # negation
        if sentence[k].token == 'plus' and sentence[k + 1].token == 'rien':
            sentence[k:k + 2] = [Word("pas", "pas", "ADV", None, None)]
            k = 0
        elif sentence[k].token == 'guère' and sentence[k + 1].token == 'plus':
            sentence[k:k + 2] = [Word("pas", "pas", "ADV", None, None)]
            k = 0
        elif sentence[k].token == 't' and sentence[k + 1].token in ["il", "elle", "on", "ils", "elles"]:
            sentence = sentence[:k] + sentence[k + 2:]
            k = 0
        elif sentence[k].token in ["n'", 'ne']:
            sentence = sentence[:k] + sentence[k + 1:]
        else:
            k += 1
    for v in range(len(sentence)):
        if sentence[v].token in ["guère", 'ni', 'rien']:
            sentence[v] = Word("pas", "pas", "ADV", None, None)
    for p in range(1, len(sentence)):
        if sentence[p].token == "pas":
            sentence[p], sentence[p - 1] = sentence[p - 1], sentence[p]
    return sentence


def check_if_mwe(word):
    if '_' in word.lemma:
        word.tag = 'MWE'


def check_if_named_entity(word):
    if word.ent_type == "MED" or word.ent_type == "PER" or word.ent_type == "LOC":
        word.tag = "NE"


def add_sense_tags_to_word(sentence_wsd, sentence):
    proc_s = re.sub(r"\s+", '|', sentence_wsd).split("|")
    wn = [proc_s[i] for i in range(1, len(proc_s), 2)]
    index = 0
    for i, w in enumerate(sentence):
        if w.tag != "NE" and w.tag != "MWE" and w.pos == "NOUN":
            w.wn = wn[i + index]
        elif w.tag == "MWE":
            num_words_in_mwe = len(w.lemma.split('_')) - 1
            index += num_words_in_mwe
    return sentence


def multiword_expression_detection_from_file(input_text, pictogram_set="arasaac"):
    """
    Function to detect multiword_expression based on existing pictograms from french Araasaac dataset.
    Requires the file : "multiwords.json" with multiwords.

    :param input_text: Input text on which the MWED will be applied
    :type input_text: str
    :param pictogram_set: Refers the selected pictogram set
    :type input_text: str
    """

    # List of every multiwords depending on the pictogram set
    multiwords = []
    multiwords_ = dict()

    output_text = input_text

    tokenized_input = input_text.split(" ")

    # Opening the JSON file where there are multiword expression regrouped by pictogram sets
    with codecs.open("database/multiwords.json", "r", encoding="utf8") as mwe_f:

        multiwords_dic = json.load(mwe_f)
        multiwords = multiwords + multiwords_dic["default"]

        # Insert beta related multiwords
        if (pictogram_set == "beta"):
            multiwords = multiwords + multiwords_dic["beta"]

        # Insert sclera related multiwords
        elif (pictogram_set == "sclera"):
            multiwords = multiwords + multiwords_dic["sclera"]

        # Insert arasaac related multiwords
        elif (pictogram_set == "arasaac"):
            multiwords = multiwords + multiwords_dic["arasaac"]
            multiwords = multiwords + multiwords_dic["temporal_expressions"]

        # Building the underscored multiword dictionary : "{word1 word2 : word1_word2}"
        for multiword in multiwords:
            multiwords_.update({multiword: multiword.replace(" ", "_")})

        # Replace every multiword expression by the underscored multiword expressions.
        occurences = re.findall('|'.join(multiwords), " ".join(input_text), flags=re.IGNORECASE)
        for el in occurences:
            output_text = re.sub(el, multiwords_[el], output_text)

    return output_text


def named_entitity_substitution(ent_type):
    """
    Function to return the lemma of substitution instead of the named entity

    :param ent_type: Type of the named entity (PER, LOC, etc.)
    :type ent_type: str
    :returns: Lemma of substitution
    :rtype: str
    """

    # Character
    if ent_type == "PER":
        return "perso"

    # City
    elif ent_type == "LOC":
        return "ville"

    # Medicine
    elif ent_type == "MED":
        return "médicaments"

    # Other or not recognized
    else:
        return ""
