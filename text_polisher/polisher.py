from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from difflib import get_close_matches
from pathlib import Path

COMMON_TYPOS = {
    'evory': 'every',
    'evry': 'every',
    'everybdy': 'everybody',
    'everyboddy': 'everybody',
    'everyboody': 'everybody',
    'hio': 'hi',
    'hii': 'hi',
    'helo': 'hello',
    'helllo': 'hello',
    'helloo': 'hello',
    'heloo': 'hello',
    'acommodate': 'accommodate', 'acheive': 'achieve', 'adress': 'address', 'agian': 'again',
    'alot': 'a lot', 'arguement': 'argument', 'becuase': 'because', 'begining': 'beginning',
    'beleive': 'believe', 'buisness': 'business', 'calender': 'calendar', 'collegue': 'colleague',
    'comming': 'coming', 'concious': 'conscious', 'definately': 'definitely', 'enviroment': 'environment',
    'experiance': 'experience', 'familar': 'familiar', 'finaly': 'finally', 'foriegn': 'foreign',
    'fourty': 'forty', 'freind': 'friend', 'goverment': 'government', 'grammer': 'grammar',
    'happend': 'happened', 'immediatly': 'immediately', 'independant': 'independent', 'knowlege': 'knowledge',
    'lenght': 'length', 'libary': 'library', 'maintainance': 'maintenance', 'neccessary': 'necessary',
    'occured': 'occurred', 'persue': 'pursue', 'publically': 'publicly', 'recieve': 'receive',
    'recieved': 'received', 'recomend': 'recommend', 'recomendation': 'recommendation', 'seperate': 'separate',
    'sucess': 'success', 'succesful': 'successful', 'successfull': 'successful', 'tommorow': 'tomorrow',
    'tommorrow': 'tomorrow', 'truely': 'truly', 'untill': 'until', 'wierd': 'weird', 'writting': 'writing',
    'thier': 'their', 'teh': 'the', 'taht': 'that', 'waht': 'what', 'whcih': 'which', 'becasue': 'because',
    'shouldnt': "shouldn't", 'wouldnt': "wouldn't", 'couldnt': "couldn't", 'cant': "can't",
    'dont': "don't", 'doesnt': "doesn't", 'didnt': "didn't", 'isnt': "isn't", 'arent': "aren't",
    'wasnt': "wasn't", 'werent': "weren't", 'havent': "haven't", 'hasnt': "hasn't", 'hadnt': "hadn't",
    'im': "I'm", 'ive': "I've", 'ill': "I'll", 'id': "I'd", 'youre': "you're", 'youve': "you've",
    'youll': "you'll", 'hes': "he's", 'shes': "she's", 'theyre': "they're", 'weve': "we've", 'lets': "let's",
}

PHRASE_FIXES = {
    'every body': 'everybody',
    'every one': 'everyone',
    'any one': 'anyone',
    'some one': 'someone',
    'no body': 'nobody',
    'good morning every body': 'good morning everybody',
    'good evening every body': 'good evening everybody',
    'good night every body': 'good night everybody',
    'informations': 'information', 'advices': 'advice', 'homeworks': 'homework', 'equipments': 'equipment',
    'researches': 'research', 'softwares': 'software', 'hardwares': 'hardware', 'furnitures': 'furniture',
    'peoples': 'people', 'childrens': 'children', 'more better': 'better', 'more easier': 'easier',
    'more faster': 'faster', 'most easiest': 'easiest', 'each others': 'each other',
    'one of my friend': 'one of my friends', 'according to me': 'in my opinion', 'discuss about': 'discuss',
    'listen me': 'listen to me', 'married with': 'married to', 'different than': 'different from',
    'good in english': 'good at English', 'interested on': 'interested in', 'depend of': 'depend on',
    'responsible of': 'responsible for', 'capable to': 'capable of', 'similar with': 'similar to',
    'in the other hand': 'on the other hand', 'make a research': 'do research', 'give an exam': 'take an exam',
    'do a decision': 'make a decision',
}

WORD_BANK_TEXT = """
a able about above accept according account across action actually add address admit after again against age ago agree air all almost alone along already also although always am among amount an and animal another answer any anyone anything appear apply area are around arrive art article as ask at available away back bad base be beautiful because become been before begin behind believe best better between big black book both break bring build business but by call came can care case cause center certain change child children choice city class clear close code college color come common company complete condition consider continue could country course create current customer dark data day demo design develop different do document down draw each early easy editor effect email end enough even ever every example exist experience explain eye face fact family far fast feel few field file final find first follow food for form found free friend from full function future game general get give go good great group gui had half hand happen hard has have he help her here high history home how however idea if important improve in include indeed industry information inside instead interest into is issue it item its itself just keep kind know language large last later learn leave left less letter life light line list little live local long look machine main make man many may me mean menu method might modern more most move much music must my name natural need never new next no not now number of off offer often old on one only open option or order other our out output over own page part people place plan point possible power practice present price process product project public put quality question quick quite rather read ready real really reason receive record redesign report result right run same save say school search section see seem send set several shape she should show simple since small so social some something sometimes sound source space special stand start state step still store style system take task team test text than that the their them then there these they thing think this those though through time to together tool top total try turn type under until up us use user useful usually value very view visual voice want was way we well went were what when where which while white who why will with within without word work world would write writing year yes you young your python github markdown tkinter json smooth balanced cleanup report clipboard corrected suggestions
"""
WORD_BANK = sorted(set(WORD_BANK_TEXT.split()) | set(COMMON_TYPOS.values()) | {'hi', 'hello', 'everybody', 'everyone', 'someone', 'anyone', 'nobody'})

@dataclass
class Edit:
    kind: str
    before: str
    after: str
    detail: str

@dataclass
class PolishResult:
    original: str
    corrected: str
    edits: list[Edit]
    warnings: list[str]

class TextPolisher:
    def __init__(self, mode: str = 'balanced'):
        self.mode = mode if mode in {'balanced', 'smooth'} else 'balanced'

    def polish(self, text: str) -> PolishResult:
        original = text
        edits: list[Edit] = []
        text = self.normalize_newlines(text)
        text = self.fix_spaces(text, edits)
        text = self.fix_greetings(text, edits)
        text = self.fix_word_typos(text, edits)
        text = self.fix_phrases(text, edits)
        text = self.fix_greetings(text, edits)
        text = self.fix_repeated_words(text, edits)
        text = self.fix_i(text, edits)
        text = self.fix_articles(text, edits)
        text = self.fix_punctuation(text, edits)
        text = self.fix_sentence_caps(text, edits)
        text = self.add_sentence_endings(text, edits)
        if self.mode == 'smooth':
            text = self.smooth_phrases(text, edits)
        text = self.cleanup(text, edits)
        warnings = self.find_possible_typos(text)
        return PolishResult(original=original, corrected=text, edits=edits, warnings=warnings)

    def normalize_newlines(self, text: str) -> str:
        return text.replace('\r\n', '\n').replace('\r', '\n')

    def keep_case(self, source: str, replacement: str) -> str:
        if source.isupper():
            return replacement.upper()
        if len(source) > 1 and source[0].isupper():
            return replacement[:1].upper() + replacement[1:]
        return replacement

    def add_edit(self, edits: list[Edit], kind: str, before: str, after: str, detail: str):
        if before != after:
            edits.append(Edit(kind, before, after, detail))

    def fix_spaces(self, text: str, edits: list[Edit]) -> str:
        before = text
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r' *\n *', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        self.add_edit(edits, 'spacing', before, text, 'Cleaned repeated spaces and blank lines')
        return text.strip()


    def fix_greetings(self, text: str, edits: list[Edit]) -> str:
        patterns = [
            (r'\b(i|hi|hii|hio)\s+(evory|evry|every)\s+body\b', 'hi everybody'),
            (r'\b(i|hi|hii|hio)\s+everybody\b', 'hi everybody'),
            (r'\b(helo|hello|helllo|helloo)\s+(evory|evry|every)\s+body\b', 'hello everybody'),
            (r'\b(helo|hello|helllo|helloo)\s+everybody\b', 'hello everybody'),
            (r'\bhelo\b', 'hello'),
            (r'\bhelllo\b', 'hello'),
            (r'\bhelloo\b', 'hello'),
            (r'\bhio\b', 'hi'),
            (r'\bhii\b', 'hi'),
        ]

        for pattern, replacement in patterns:
            regex = re.compile(pattern, re.IGNORECASE)

            def repl(match, fixed=replacement):
                before = match.group(0)
                after = self.keep_case(before, fixed)
                edits.append(Edit('spelling', before, after, 'Corrected a greeting phrase'))
                return after

            text = regex.sub(repl, text)

        return text

    def fix_word_typos(self, text: str, edits: list[Edit]) -> str:
        def repl(match):
            word = match.group(0)
            low = word.lower()
            if low not in COMMON_TYPOS:
                return word
            corrected = self.keep_case(word, COMMON_TYPOS[low])
            edits.append(Edit('spelling', word, corrected, 'Corrected a common misspelling'))
            return corrected
        return re.sub(r"\b[A-Za-z]+(?:'[A-Za-z]+)?\b", repl, text)

    def fix_phrases(self, text: str, edits: list[Edit]) -> str:
        for wrong, right in PHRASE_FIXES.items():
            pattern = re.compile(r'\b' + re.escape(wrong) + r'\b', re.IGNORECASE)
            def repl(match, fixed=right):
                before = match.group(0)
                after = self.keep_case(before, fixed)
                edits.append(Edit('grammar', before, after, 'Replaced an unnatural phrase'))
                return after
            text = pattern.sub(repl, text)
        return text

    def fix_repeated_words(self, text: str, edits: list[Edit]) -> str:
        pattern = re.compile(r'\b([A-Za-z]+)\s+\1\b', re.IGNORECASE)
        def repl(match):
            before = match.group(0)
            after = match.group(1)
            edits.append(Edit('grammar', before, after, 'Removed a repeated word'))
            return after
        return pattern.sub(repl, text)

    def fix_i(self, text: str, edits: list[Edit]) -> str:
        before = text
        text = re.sub(r'\bi\b', 'I', text)
        self.add_edit(edits, 'capitalization', before, text, 'Capitalized standalone I')
        return text

    def starts_with_vowel_sound(self, word: str) -> bool:
        word = word.lower()
        if word.startswith(('honest', 'hour', 'heir', 'honor')):
            return True
        if word.startswith(('university', 'unique', 'user', 'useful', 'european', 'one', 'once')):
            return False
        return bool(word) and word[0] in 'aeiou'

    def fix_articles(self, text: str, edits: list[Edit]) -> str:
        pattern = re.compile(r'\b(a|an)\s+([A-Za-z]+)', re.IGNORECASE)
        def repl(match):
            article, word = match.group(1), match.group(2)
            wanted = 'an' if self.starts_with_vowel_sound(word) else 'a'
            if article.lower() == wanted:
                return match.group(0)
            if article[0].isupper():
                wanted = wanted.capitalize()
            before = match.group(0)
            after = wanted + ' ' + word
            edits.append(Edit('grammar', before, after, 'Adjusted a/an before the next word'))
            return after
        return pattern.sub(repl, text)

    def fix_punctuation(self, text: str, edits: list[Edit]) -> str:
        before = text
        text = re.sub(r'\s+([,.;:!?])', r'\1', text)
        text = re.sub(r'([,.;:!?])([A-Za-z])', r'\1 \2', text)
        text = re.sub(r'([,.;:!?])\1+', r'\1', text)
        self.add_edit(edits, 'punctuation', before, text, 'Fixed spacing around punctuation')
        return text

    def fix_sentence_caps(self, text: str, edits: list[Edit]) -> str:
        chars = list(text)
        make_upper = True
        for i, char in enumerate(chars):
            if char.isalpha() and make_upper:
                chars[i] = char.upper()
                make_upper = False
            elif char in '.!?\n':
                make_upper = True
        new_text = ''.join(chars)
        self.add_edit(edits, 'capitalization', text, new_text, 'Capitalized sentence beginnings')
        return new_text

    def add_sentence_endings(self, text: str, edits: list[Edit]) -> str:
        parts = re.split(r'(\n+)', text)
        built = []
        for part in parts:
            if not part or part.startswith('\n'):
                built.append(part)
                continue
            stripped = part.rstrip()
            if stripped and stripped[-1] not in '.!?:':
                edits.append(Edit('punctuation', part, stripped + '.', 'Added ending punctuation'))
                part = stripped + '.'
            built.append(part)
        return ''.join(built)

    def smooth_phrases(self, text: str, edits: list[Edit]) -> str:
        replacements = {
            r'\bI think that\b': 'I think',
            r'\bIt is very very\b': 'It is very',
            r'\bA lot of of\b': 'A lot of',
        }
        for pattern, replacement in replacements.items():
            new_text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            self.add_edit(edits, 'style', text, new_text, 'Smoothed a repetitive phrase')
            text = new_text
        return text

    def cleanup(self, text: str, edits: list[Edit]) -> str:
        before = text
        text = re.sub(r' +', ' ', text)
        text = re.sub(r' ([,.;:!?])', r'\1', text)
        text = text.strip()
        self.add_edit(edits, 'cleanup', before, text, 'Final cleanup')
        return text

    def find_possible_typos(self, text: str) -> list[str]:
        warnings = []
        seen = set()
        for word in re.findall(r'\b[A-Za-z]{4,}\b', text):
            low = word.lower()
            if low in seen:
                continue
            seen.add(low)
            if low in WORD_BANK:
                continue
            suggestion = get_close_matches(low, WORD_BANK, n=1, cutoff=0.87)
            if suggestion:
                warnings.append(f'{word} may be close to {suggestion[0]}')
        return warnings[:30]


def format_report(result: PolishResult) -> str:
    lines = ['Corrected text', '=' * 60, result.corrected, '']
    if result.edits:
        lines.extend(['Changes', '=' * 60])
        for i, edit in enumerate(result.edits, 1):
            lines.append(f"{i}. [{edit.kind}] {edit.before!r} -> {edit.after!r}")
            lines.append(f"   {edit.detail}")
        lines.append('')
    if result.warnings:
        lines.extend(['Possible spelling suggestions', '=' * 60])
        for warning in result.warnings:
            lines.append('- ' + warning)
        lines.append('')
    return '\n'.join(lines)


def run_cli() -> int:
    parser = argparse.ArgumentParser(prog='text-polisher', description='Correct and polish English text locally.')
    parser.add_argument('text', nargs='*', help='Text to correct')
    parser.add_argument('-f', '--file', help='Read text from a file')
    parser.add_argument('-o', '--output', help='Save corrected text to a file')
    parser.add_argument('--report', action='store_true', help='Print a detailed report')
    parser.add_argument('--json', action='store_true', help='Print JSON output')
    parser.add_argument('--mode', choices=['balanced', 'smooth'], default='balanced', help='Correction mode')
    args = parser.parse_args()

    if args.file:
        text = Path(args.file).read_text(encoding='utf-8')
    elif args.text:
        text = ' '.join(args.text)
    else:
        text = sys.stdin.read()

    result = TextPolisher(mode=args.mode).polish(text)

    if args.output:
        Path(args.output).write_text(result.corrected, encoding='utf-8')

    if args.json:
        print(json.dumps({
            'original': result.original,
            'corrected': result.corrected,
            'edits': [asdict(edit) for edit in result.edits],
            'warnings': result.warnings,
        }, indent=2, ensure_ascii=False))
    elif args.report:
        print(format_report(result))
    else:
        print(result.corrected)
    return 0

if __name__ == '__main__':
    raise SystemExit(run_cli())
