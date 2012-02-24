from unittest import TestCase
from haikus import HaikuText
from haikus.evaluators import HaikuEvaluator, NounVerbAdjectiveLineEndingEvaluator, \
    JoiningWordLineEndingEvaluator, EndsInNounEvaluator, PrepositionCountEvaluator


class TestHaikuText(TestCase):
     def test_calculate_quality(self):
        comment = HaikuText(text="Not a haiku")       
        comment2 = HaikuText(text="An old silent pond... A frog jumps into the pond. Splash! Silence again.")

        #some 'dummy' evaluators
        class MediocreHaikuEvaluator(HaikuEvaluator):
            def evaluate(self, comment):
                return 50

        default = (HaikuEvaluator, 1)
        mediocre = (MediocreHaikuEvaluator, 1)

        #Not even remotely a haiku, quality == 0
        self.assertEqual(comment.calculate_quality(), 0)
        #Still 0 with dumb_evaluator
        self.assertEqual(comment.calculate_quality(evaluators=[default,]), 0)

        #It's a haiku, check its quality
        self.assertEqual(comment2.calculate_quality(evaluators=[default,]), 100)
        #Evaluators are averaged
        self.assertEqual(comment2.calculate_quality(evaluators=[default, mediocre]), 150/2)

class EvaluatorsTest(TestCase):   
    def test_line_ending_nva_evaluator(self):
        """
        Test that the line noun/verb/adjective ending part-of-speech evaluator 
        gives the expected scores to haikus
        """
        pos_evaluator = NounVerbAdjectiveLineEndingEvaluator()
        
        #comment with 2 lines that end in noun/verbs
        text = HaikuText(text="An old silent pond... A frog jumps into the pond. Splash! Silence again.")
        #should score 66
        self.assertEqual(pos_evaluator(text), 66)

        # 1 verb, 1 noun, 1 pronoun
        text.set_text("Application is the most wonderful artist that man can show us")
        #should score 66
        self.assertEqual(pos_evaluator(text), 2*100/3) 
               
        #No verbs/nouns at line ends,
        text.set_text("They jumped ship on us the boat is very never that man can show us")
        self.assertEqual(pos_evaluator(text), 0) 

    def test_joining_words_line_ending_evaluator(self):
        """
        Test that the joining words line ending evaluator give the correct scores to haikus
        with and without "joining" words at the end of lines.
        """
        join_evaluator = JoiningWordLineEndingEvaluator()
        
        #comment with 2 lines that end in noun/verbs
        text = HaikuText(text="An old silent pond... A frog jumps into the pond. Splash! Silence again.")
        #should score 100 
        self.assertEqual(join_evaluator(text), 100)

        # 2 good lines, one ending in is
        text.set_text("Application and the most wonderful artist that man can show us")
        #should score 66
        self.assertEqual(join_evaluator(text), 2*100/3) 
               
        #No verbs/nouns at line ends,
        text.set_text("They jumped right on in the boat is never sunk and that man can show of")        
        self.assertEqual(join_evaluator(text), 0)

    def test_ends_in_noun_evaluator(self):
        """
        Test that the EndsInNounEvaluator boosts the score of haikus that end in a noun
        """
        noun_evaluator = EndsInNounEvaluator()
        
        #Doesn't end in a noun
        text = HaikuText(text="An old silent pond... A frog jumps into the pond. Splash! Silence again.")
        #should score 0
        self.assertEqual(noun_evaluator(text), 0)

        #Ends in a pronoun
        text.set_text("Application is the most wonderful artist that man can show us")
        #should score 100
        self.assertEqual(noun_evaluator(text), 100)

        #Ends in a noun
        text.set_text("Application is the most wonderful artist that man can show god")
        #should score 100
        self.assertEqual(noun_evaluator(text), 100)

class PrepositionalCountEvaluatorTest(TestCase):
    """
    Test the preposition count evaluator.
    """
    def setUp(self):
        self.comment_a = HaikuText(text="Dog in the floor at, one onto the home for it, jump into the pool")
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
        score = self.comment_a.calculate_quality(evaluators=[(PrepositionCountEvaluator, 1)])
        self.assertEquals(score, 0)

        """
        Test B:
            this is a new vogue, she always has a new vogue, she never repeats
            0 prepositions
            15 words
        """
        assert self.comment_b.has_haiku() is True
        score = self.comment_b.calculate_quality(evaluators=[(PrepositionCountEvaluator, 1)])
        self.assertEquals(score, 99)
        
class BigramExtraction(TestCase):
    def setUp(self):
        self.comment = HaikuText(text="Dog in the floor at, one onto the home for it, jump into the pool")
    
    def test_bigram_extraction(self):
        bigrams = self.comment.line_end_bigrams()
        self.assertEquals((('at', 'one'), ('it', 'jump')), bigrams)


class UnknownWordHandling(TestCase):
    def test_handle_unknown(self):
        haiku = HaikuText(text="this is a new vogue, she always has a new vogue, she never foobaz")
        #foobar is not in cmudict!
        from haikus.haikutext import WORD_DICT
        self.assertEqual(WORD_DICT.get("foobaz"), None)

        #however, we can count 2 syllables in it anyhow
        self.assertTrue((2, "foobaz") in haiku.syllable_map())

class HaikuIsFullSentenceEvaluatorTest(TestCase):
    """
    Test the haiku is full sentence evaluation
    """
    pass

class LineIsFullSentenceEvaluatorTest(TestCase):
    """
    """
    pass

class LineEndsInPunctuationEvaluatorTest(TestCase):
    """
    """
    pass
    
