import math
from unittest import TestCase
from haikus import HaikuText
from haikus.evaluators import HaikuEvaluator, NounVerbAdjectiveLineEndingEvaluator, \
    JoiningWordLineEndingEvaluator, EndsInNounEvaluator, PrepositionCountEvaluator


class TestHaiku(TestCase):
     def test_calculate_quality(self):
        haiku = HaikuText(text="An old silent pond... A frog jumps into the pond. Splash! Silence again.").get_haiku()

        #some 'dummy' evaluators
        class MediocreHaikuEvaluator(HaikuEvaluator):
            def evaluate(self, haiku):
                return 50

        default = (HaikuEvaluator, 1)
        mediocre = (MediocreHaikuEvaluator, 1)

        #It's a haiku, check its quality
        self.assertEqual(haiku.calculate_quality(evaluators=[default,]), 100)

        #Evaluators are averaged
        self.assertEqual(haiku.calculate_quality(evaluators=[default, mediocre]), 150/2)

     

class EvaluatorsTest(TestCase):   
    def test_line_ending_nva_evaluator(self):
        """
        Test that the line noun/verb/adjective ending part-of-speech evaluator gives the expected scores to haikus
        """
        pos_evaluator = NounVerbAdjectiveLineEndingEvaluator()
        
        #comment with 2 lines that end in noun/verbs
        text = HaikuText(text="An old silent pond... A frog jumps into the pond. Splash! Silence again.")
        haiku = text.get_haiku()
        #should score 66
        self.assertEqual(pos_evaluator(haiku), 66)

        # 1 verb, 1 noun, 1 pronoun
        text.set_text("Application is the most wonderful artist that man can show us")
        haiku = text.get_haiku()
        #should score 66
        self.assertEqual(pos_evaluator(haiku), 2*100/3) 
               
        #No verbs/nouns at line ends,
        text.set_text("They jumped ship on us the boat is very never that man can show us")
        haiku = text.get_haiku()
        
        self.assertEqual(pos_evaluator(haiku), 0) 

    def test_joining_words_line_ending_evaluator(self):
        """
        Test that the joining words line ending evaluator give the correct scores to haikus
        with and without "joining" words at the end of lines.
        """
        join_evaluator = JoiningWordLineEndingEvaluator()
        
        #comment with 2 lines that end in noun/verbs
        text = HaikuText(text="An old silent pond... A frog jumps into the pond. Splash! Silence again.")
        haiku = text.get_haiku()
        #should score 66 
        self.assertEqual(join_evaluator(haiku), 100)

        # 2 good lines, one ending in is
        text.set_text("Application and the most wonderful artist that man can show us")
        haiku = text.get_haiku()
        #should score 66
        self.assertEqual(join_evaluator(haiku), 2*100/3) 
               
        #No verbs/nouns at line ends,
        text.set_text("They jumped right on in the boat is never sunk and that man can show of")
        haiku = text.get_haiku()
        
        self.assertEqual(join_evaluator(haiku), 0)

    def test_ends_in_noun_evaluator(self):
        """
        Test that the EndsInNounEvaluator boosts the score of haikus that end in a noun
        """
        noun_evaluator = EndsInNounEvaluator()
        
        #Doesn't end in a noun
        text = HaikuText(text="An old silent pond... A frog jumps into the pond. Splash! Silence shopping")
        haiku = text.get_haiku()
        #should score 0
        self.assertEqual(noun_evaluator(haiku), 0)

        #Ends in a pronoun
        text.set_text("Application is the most wonderful artist that man can show us")
        haiku = text.get_haiku()
        #should score 100
        self.assertEqual(noun_evaluator(haiku), 100)

        #Ends in a noun
        text.set_text("Application is the most wonderful artist that man can show god")
        haiku = text.get_haiku()
        #should score 100
        self.assertEqual(noun_evaluator(haiku), 100)

class PrepositionalCountEvaluatorTest(TestCase):
    """
    Test the preposition count evaluator.
    """
    def setUp(self):
        self.comment_a = HaikuText(text="Dog in the floor mat, one onto the home for it, jump into the pool")
        self.comment_b = HaikuText(text="this is a new vogue, she always has a new vogue, she never repeats")
    
    def test_preposition_count(self):
        """
        Test A:
            Dog in the floor at, one onto the home for it, jump into the pool
                **           **      ****          ***          ****
            
            5 prepositions
            15 words
        """
        assert self.comment_a.has_haiku() is True
        score = self.comment_a.get_haiku().calculate_quality(evaluators=[(PrepositionCountEvaluator, 1)])
        self.assertEquals(score, 100 - math.exp(4))

        """
        Test B:
            this is a new vogue, she always has a new vogue, she never repeats
            0 prepositions
            15 words
        """
        assert self.comment_b.has_haiku() is True
        score = self.comment_b.get_haiku().calculate_quality(evaluators=[(PrepositionCountEvaluator, 1)])
        self.assertEquals(score, 99)
        
class BigramExtraction(TestCase):
    def setUp(self):
        self.comment = HaikuText(text="Dog in the floor at, one onto the home for it, jump into the pool")
        self.haiku = self.comment.get_haiku()
    def test_bigram_extraction(self):
        bigrams = self.haiku.line_end_bigrams()
        self.assertEquals((('at', 'one'), ('it', 'jump')), bigrams)


class UnknownWordHandling(TestCase):
    def test_handle_unknown(self):
        haiku = HaikuText(text="this is a new vogue, she always has a new vogue, she never foobaz")
        #foobar is not in cmudict!
        from haikus.haikutext import WORD_DICT
        self.assertEqual(WORD_DICT.get("foobaz"), None)

        #however, we can count 2 syllables in it anyhow
        self.assertTrue((2, "foobaz") in haiku.syllable_map())    
