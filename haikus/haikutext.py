"""
Classes and utilities for extracting haiku from arbitrary text and evaluating them based on some programmatically
defined criteria
"""
import nltk
import string
from nltk.corpus import cmudict
from nltk_contrib.readability import syllables_en
from haikus.evaluators import DEFAULT_HAIKU_EVALUATORS

global WORD_DICT
WORD_DICT = cmudict.dict()

class HaikuText(object):
    """
    A wrapper around some sequence of text
    """
    def __init__(self, text=None):
        self._text = text
        
    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = text

    def filtered_text(self):
        """
        Strip punctuation from this text
        """
        exclude = set(string.punctuation).difference(set("'"))
        s = ''.join(ch for ch in self.get_text() if ch not in exclude)
        return s

    def filtered_word(self, word):
        """
        Strip punctation from the given token so we can look it up in
        our word dictionary
        """
        exclude = set(string.punctuation).difference(set("'"))
        filtered = ''.join(ch for ch in word if ch not in exclude)
        return filtered
    
    def word_syllables(self, word, override_word=None):
        """
        Get the syllable count for the given word, according to WORD_DICT
        """
        word = word.encode('ascii', 'ignore').strip().lower()
        try:
            matches = WORD_DICT[self.filtered_word(word)]
            for tree in matches:
                return (len([phoneme for phoneme in tree if phoneme[-1].isdigit()]), word)
        except KeyError:
            return self.unknown_word_handler(word)

    def syllable_map(self, strip_punctuation=False):
        """
        Map words in this text to their syllable count
        """
        if strip_punctuation:
            s = self.filtered_text()
        else:
            s = self.get_text()
        return map(self.word_syllables, s.split())
                
    def syllable_count(self):
        """
        Sum the syllable counts for all words in this text
        """
        return sum([t[0] for t in self.syllable_map()])

    def line_end_bigrams(self):
        """
        Find the bigrams that occur across any two lines in this text's
        haiku
        """
        bigrams = ()
        if self.has_haiku():
            lines = [line.split(" ") for line in self.haiku()]
            bigrams = ((self.filtered_word(lines[0][-1]), self.filtered_word(lines[1][0])),
                       (self.filtered_word(lines[1][-1]), self.filtered_word(lines[2][0])))
        return bigrams
    
    def haiku(self, strip_punctuation=False):
        """
        Find a haiku in this text
        """
        haiku = [5, 12, 17]
        cumulative = [0]
        syllable_map = self.syllable_map(strip_punctuation=strip_punctuation)
        for w in syllable_map:
            cumulative.append(cumulative[-1] + w[0])
        cumulative = cumulative[1:]
        is_haiku = set(cumulative).intersection(haiku) == set(haiku)
        
        if is_haiku:
            lookup = dict((v,k) for k, v in enumerate(cumulative))
            enum_lookup = list(enumerate(lookup))
            start = 0
            lines = []
            for line in haiku:
                section = syllable_map[start:lookup[line]+1]
                words = [s[1] for s in section]
                lines.append(' '.join(words))
                try:
                    start = enum_lookup[lookup[line] + 1][0]
                except IndexError:
                    pass
            return lines
        else:
            return False
        
    def has_haiku(self):
        """
        Return True if this text contains a haiku
        """
        return bool(self.haiku())
    
    def calculate_quality(self, evaluators=None):
        """
        Calculate the score of this text's haiku across a list of evaluators
        and return the mean average.
        """
        if evaluators is None:
            evaluators = DEFAULT_HAIKU_EVALUATORS
        score = 0
        if self.has_haiku():
            for evaluator_class, weight in evaluators:
                evaluator = evaluator_class(weight=weight)
                score += evaluator(self)
            try:
                score /= sum([weight for evaluator, weight in evaluators])
            except ZeroDivisionError:
                return 0
        return score

    def unknown_word_handler(self, word):
        """
        handle words outside of cmudict by attempting to count their syllables
        """
        syllable_count = syllables_en.count(self.filtered_word(word))
        if syllable_count > 0:
            return (syllable_count, word)
        else:
            #give the word 1 syllable as it's probably something like f*** or thbpt!
            return (1, word)
