import unittest
from text_polisher import TextPolisher

class TextPolisherTests(unittest.TestCase):
    def setUp(self):
        self.polisher = TextPolisher()

    def test_common_typo(self):
        result = self.polisher.polish('i recieve alot of informations')
        self.assertEqual(result.corrected, 'I receive a lot of information.')

    def test_repeated_word(self):
        result = self.polisher.polish('This is is a test')
        self.assertEqual(result.corrected, 'This is a test.')

    def test_article_fix(self):
        result = self.polisher.polish('this is a apple and an university')
        self.assertEqual(result.corrected, 'This is an apple and a university.')

    def test_punctuation_spacing(self):
        result = self.polisher.polish('hello ,world')
        self.assertEqual(result.corrected, 'Hello, world.')

    def test_phrase_fix(self):
        result = self.polisher.polish('i am interested on python')
        self.assertEqual(result.corrected, 'I am interested in python.')

    def test_smooth_mode(self):
        result = TextPolisher(mode='smooth').polish('i think that this is very very good')
        self.assertEqual(result.corrected, 'I think this is very good.')

    def test_greeting_typo_line(self):
        result = self.polisher.polish('i evory body\nhio')
        self.assertEqual(result.corrected, 'Hi everybody.\nHi.')

    def test_hello_everybody(self):
        result = self.polisher.polish('helo every body')
        self.assertEqual(result.corrected, 'Hello everybody.')

if __name__ == '__main__':
    unittest.main()
