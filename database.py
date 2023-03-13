import pandas as pd


def load_picto_table(filepath):
    """
    Function to load a pictogram table from a csv file

    :param filepath: Path of the csv file containing the pictogram table
    :type filepath: str
    :returns: Dictionay containing the table with : lemma as key, list of pictogram information as value
    :rtype: dict
    """

    try:
        # Read the csv file with pandas
        df = pd.read_csv(filepath)

        picto_table = df[['idpicto', 'lemma', 'synset', 'synset2']].copy()
        picto_table.loc[:, 'synset2_proc'] = picto_table['synset2'].apply(lambda a: a.split('-')[0])

        print("*** Pictogram table loaded : " + filepath + " ***")

        return picto_table

    except IOError:
        print("Could not read file, wrong file format.", filepath)
        return


def parse_wn31_file(file):
    """Parse le fichier index.sense de wordnet 3.1"""
    try:
        data_wn31 = pd.read_csv(file, delimiter=" ", names=["sense_key", "synset", "id1", "id2"], header=None)
        return data_wn31
    except IOError:
        print("Could not read file, wrong file format.", file)
        return


def get_synset_from_sense_key(wn_data, sense_key):
    if not wn_data.loc[wn_data['sense_key'] == sense_key]["synset"].tolist():
        return []
    else:
        return str(wn_data.loc[wn_data['sense_key'] == sense_key]["synset"].tolist()[0])


def get_sense_key_from_synset(wn_data, synset_key):
    if not wn_data.loc[wn_data['synset'] == int(synset_key)]["sense_key"].tolist():
        return []
    else:
        return str(wn_data.loc[wn_data['synset'] == int(synset_key)]["sense_key"].tolist()[0])


def get_sense_keys_from_synset_wolf(wn_data, picto_table, synset_wolf):
    synset_ids_from_synset_wolf = list(
        set(picto_table.loc[picto_table['synset'] == synset_wolf]["synset2_proc"].tolist()))
    sense_keys = []
    for synset in synset_ids_from_synset_wolf:
        sense_key = get_sense_key_from_synset(wn_data, synset)
        sense_keys.append(sense_key)
    return sense_keys


def get_arasaac_picto_by_wn(wn_data, picto_table, sense_key):
    try:
        if sense_key:
            synset = get_synset_from_sense_key(wn_data, sense_key)
            if not synset:
                return [None]
            else:
                synset = str(synset).zfill(8)
                picto_ids_from_wn = list(
                    set(picto_table.loc[picto_table['synset2_proc'] == synset]["idpicto"].tolist()))
            if not picto_ids_from_wn:
                return [None]
            else:
                return picto_ids_from_wn
        else:
            return [None]
    # Else, returns the unknown id (-1)
    except Exception:
        return -1


def get_araasac_picto_id_by_lemma(picto_table, lemma, pos):
    """
    Function to get the pictogram id from its word as input

    :param word: Input word
    :type word: Class `Word`
    :returns: Arasaac id of the associated pictogram
    :rtype: str
    """

    # If the word exists in the pictogram table
    try:
        picto_ids_from_lemma = list(set(picto_table.loc[picto_table['lemma'] == lemma]["idpicto"].tolist()))
        if not picto_ids_from_lemma:
            return [None]
        elif lemma == "pas" and pos == "ADV":
            picto_ids_from_lemma = [5526]
        return picto_ids_from_lemma
    # Else, returns the unknown id (-1)
    except Exception:
        return -1

def get_lemma_by_id_picto(picto_table, id_picto):
    try:
        picto_lemma = list(set(picto_table.loc[picto_table['idpicto'] == id_picto]["lemma"].tolist()))
        if not picto_lemma:
            return ""
        return picto_lemma[0]
    except Exception:
        return -1