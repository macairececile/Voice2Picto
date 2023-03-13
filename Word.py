class Word():
    """Representation of a word and its associated information from applied shallow analysis pipeline.

    :param lemma: Lemma of the word
    :type lemma: str
    :param pos: POS Tag of the word
    :type pos: str
    :param ent_type: Type of the named entity
    :type ent_type: str, Optional
    """

    def __init__(self, token, lemma, pos, ent_type=None, tag=None, wn=None):
        """
        Constructor method
        """
        self.token = token
        self.lemma = lemma
        self.pos = pos
        self.tag = tag
        self.wn = wn

        # Named Entity
        if (ent_type):
            self.ent_type = ent_type
        else:
            self.ent_type = None

        self.ent_text = None

    def __str__(self):
        """
        Print method
        """

        result = ""

        if (self.lemma):
            result = f"LEMMA : {self.lemma}  "

        if (self.pos):
            result = result + f"POS : {self.pos}  "

        if (self.ent_type):
            result = result + f"ENT : {self.ent_type}  "

        if (self.ent_text):
            result = result + f"TEXT : {self.ent_text}"

        return result

    def add_wn(self, wn):
        self.wn = wn
