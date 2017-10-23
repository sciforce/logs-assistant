import json
from pathlib import Path
from collections import Counter

from logs_analyzer.chatbot.actions.responses import Responses
from logs_analyzer.chatbot.tokenizer import Tokenizer
from logs_analyzer.chatbot import BotState
from logs_analyzer.chatbot.actions.high_level_actions import HighLevelActions


class ActionClassifier:
    def __init__(self, service_names):
        with (Path(__file__).parents[3] / 'data' / 'intents.json').open('r') as intents_file:
            self.intents = json.load(intents_file)
        self.tokenizer = Tokenizer(dict([(x, Tokenizer.SERVICE) for x in service_names]))
        self.all_keywords = Counter()
        for elements in self.intents.values():
            elements['keywords'] = Counter()
            for ex in elements['examples']:
                words = [self.tokenizer.process_word(x) for x in ex.split()]
                elements['keywords'].update(words)
                self.all_keywords.update(words)

    def classify(self, phrase):
        phrase = self.tokenizer.replace_dates(phrase)
        words = self.tokenizer.eliminate_skip_chars(phrase).split()
        words = set([self.tokenizer.process_word(x) for x in words])
        all_scores = {}
        for name, elements in self.intents.items():
            score = 0
            for w in words:
                score += elements['keywords'][w] / (self.all_keywords[w] + 1e-6)  # TF-IDF
            all_scores[name] = score
        return 'unknown' if max(all_scores.values()) < 0.01 else max(all_scores, key=all_scores.get)

    def extract_integer(self, phrase):
        phrase = self.tokenizer.replace_dates(phrase)
        orig_words = self.tokenizer.eliminate_skip_chars(phrase).split()
        words = [self.tokenizer.process_word(x) for x in orig_words]
        numbers = []
        for wi, w in enumerate(words):
            if w == Tokenizer.NUMBER.lower():
                numbers.append(int(orig_words[wi]))
        return numbers

    def extract_date(self, phrase):
        dates = []
        words = phrase.split()
        max_num_words = 5
        current_start = 0
        current_len = max_num_words
        while current_start < len(words):
            current_text = ' '.join(words[current_start:current_start+current_len])
            if len(current_text) > 2:
                parsed = Tokenizer.date_parser(current_text)
            else:
                parsed = None
            if parsed is None and current_len == 1:
                current_start += 1
                current_len = max_num_words
            elif parsed is None:
                current_len -= 1
            else:
                dates.append(parsed)
                current_start += current_len
        return dates

    def extract_service(self, phrase):
        orig_words = self.tokenizer.eliminate_skip_chars(phrase).split()
        words = [self.tokenizer.process_word(x) for x in orig_words]
        services = []
        for wi, w in enumerate(words):
            if w == Tokenizer.SERVICE.lower():
                services.append(orig_words[wi])
        return services


if __name__ == '__main__':
    import pickle
    with (Path(__file__).parents[3] / 'data' / 'reader.pickle').open('rb') as f:
        data = pickle.load(f)
    debug = True
    state = BotState(data.logs)
    classifier = ActionClassifier(state.all_data['service'].unique())
    actions = HighLevelActions(state)
    responses = Responses(state, classifier.intents)
    while True:
        text = input('Enter query:\n')
        intent = classifier.classify(text)
        if debug:
            print('[D] Detected intent: {}'.format(intent))

        state.integer_params = classifier.extract_integer(text)
        state.date_params = classifier.extract_date(text)
        state.service_params = classifier.extract_service(text)
        if debug:
            print('[D] Integer params: {}'.format(', '.join([str(x) for x in state.integer_params])))
            print('[D] Date params: {}'.format(', '.join([str(x) for x in state.date_params])))
            print('[D] Service params: {}'.format(', '.join([str(x) for x in state.service_params])))
        actions.call_action(intent)
        responses.show_response(intent)
