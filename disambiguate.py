from method.neural.NeuralDisambiguator import NeuralDisambiguator
from ufsac.ufsac.core.Word import Word
from ufsac.ufsac.core.Sentence import Sentence
from ufsac.common.WordnetHelper import WordnetHelper
from ufsac.common.XMLHelper import XMLHelper


def linguistic_processing(sentence):
    """
        Function to clean the sentence (replace special characters)
        :param sentence: string
        :returns: cleaned sentence (str)
    """
    return sentence.replace("'", "' ").replace("-", " ")


def process_out_asr_for_wsd(text):
    sent = Sentence()

    text = text.split(' ')
    for word in text:
        w_proc = Word(XMLHelper.from_valid_xml_entity(word.lower()))
        sent.add_word(w_proc)
    return [sent]


def disambiguate(text, neural_disambiguator):
    """
        Function to disambiguate predicted hypothesis from asr model and store in dict
        :param data_path: path of the data from the wsd model
        :param weights: path of the wsd model
        :param text: sentence from the asr output
        :return disambiguate sentence
    """
    sentence_proc = linguistic_processing(text)
    sentence = process_out_asr_for_wsd(sentence_proc)

    neural_disambiguator.disambiguate_dynamic_sentence_batch(sentence, "wsd_test")
    sentence_wsd = ""
    for word in sentence[0].get_words():
        sentence_wsd += word.get_value().replace("|", "/")
        if word.has_annotation("wsd_test"):
            sentence_wsd += "|" + word.get_annotation_value("wsd_test")
        sentence_wsd += " "
    return sentence_proc, sentence_wsd
