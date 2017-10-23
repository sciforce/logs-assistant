from collections import Counter
import re
import numpy as np
import dateparser


class Tokenizer:
    NUMBER = '_NUM'
    DATE = '_DATE'
    SERVICE = '_SERVICE'
    UNKNOWN = '_UNK'

    def __init__(self, substitutions=None):
        self.keep_words = 100
        self.vocabulary = {}
        self.counter = Counter()
        self.digits = re.compile('\d+')
        self.skip_chars = '\t\n:.,"?!'
        self.substitutions = substitutions or {}

    def process_word(self, word):
        w = word.lower()
        w = self.digits.sub(Tokenizer.NUMBER, w)
        for sub_what, sub_with in self.substitutions.items():
            w = w.replace(sub_what, sub_with)
        return w.lower()

    @staticmethod
    def date_parser(string):
        return dateparser.parse(string, languages=['en'])

    def replace_dates(self, string):
        result = []
        words = string.split()
        max_num_words = 5
        current_start = 0
        current_len = max_num_words
        while current_start < len(words):
            current_text = ' '.join(words[current_start:current_start + current_len])
            if len(current_text) > 2:
                parsed = Tokenizer.date_parser(current_text)
            else:
                parsed = None
            if parsed is None and current_len == 1:
                result.append(words[current_start])
                current_start += 1
                current_len = max_num_words
            elif parsed is None:
                current_len -= 1
            else:
                result.append(Tokenizer.DATE)
                current_start += current_len
        return ' '.join(result)

    def eliminate_skip_chars(self, string):
        for c in self.skip_chars:
            string = string.replace(c, ' ')
        return string.replace('  ', ' ')

    def extend_vocabulary(self, string):
        string = self.replace_dates(string)
        string = self.eliminate_skip_chars(string)
        words = [self.process_word(x) for x in string.split()]
        words = [w for w in words if w]
        self.counter.update(words)

    def build_vocabulary(self):
        vocab = self.counter.most_common(self.keep_words)
        self.vocabulary.clear()
        self.vocabulary[Tokenizer.UNKNOWN] = 0
        self.vocabulary[Tokenizer.NUMBER] = 1
        for w, _ in vocab:
            self.vocabulary[w] = len(self.vocabulary)

    def tokenize(self, string):
        words = [self.process_word(x) for x in string.split()]
        return [(self.vocabulary[w] if w in self.vocabulary else self.vocabulary[Tokenizer.UNKNOWN]) for w in words]

    def get_bag_of_words(self, document):
        elements = self.tokenize(document)
        vector = np.zeros(shape=[1, len(self.vocabulary) + 1], dtype=np.float32)
        for elem_id in elements:
            vector[0, elem_id] += 1
        return vector


if __name__ == '__main__':
    from logs_analyzer.reader import LogsReader
    from tqdm import tqdm
    from logs_analyzer.chatbot.entry_classifier import EntryClassifier
    import pickle
    import matplotlib.pyplot as plt
    print('Loading log files...')
    try:
        with open('../../data/reader.pickle', 'rb') as f:
            reader = pickle.load(f)
    except FileNotFoundError:
        reader = LogsReader({'foo': 'foo.log',
                             'bar': 'bar.log',
                             'foobar': 'foobar.log'})
        with open('../../data/reader.pickle', 'wb') as f:
            pickle.dump(reader, f)
    print('Tokenizing...')
    try:
        with open('../../data/tokenizer.pickle', 'rb') as f:
            t = pickle.load(f)
    except FileNotFoundError:
        t = Tokenizer()
        for message in tqdm(reader.logs['message']):
            t.extend_vocabulary(message)
        t.build_vocabulary()
        with open('../../data/tokenizer.pickle', 'wb') as f:
            pickle.dump(t, f)
    print('Creating bag of words...')
    try:
        with open('../../data/bow.pickle', 'rb') as f:
            data = pickle.load(f)
    except FileNotFoundError:
        data = np.zeros([len(reader.logs), len(t.vocabulary) + 1], dtype=np.float32)
        for index, message in tqdm(enumerate(reader.logs['message']), total=len(reader.logs['message'])):
            data[index, :] = t.get_bag_of_words(message)
        with open('../../data/bow.pickle', 'wb') as f:
            pickle.dump(data, f)
    print('Clustering...')
    try:
        with open('../../data/clusters.pickle', 'rb') as f:
            ek = pickle.load(f)
    except FileNotFoundError:
        ek = EntryClassifier(40)
        ek.fit(data)
        with open('../../data/clusters.pickle', 'wb') as f:
            pickle.dump(ek, f)
    classes = ek.transform(data)
    print('Visualising...')
    msgs = [x for x in reader.logs['message']]
    class_labels = [(msgs[np.argwhere(classes == ci)[0][0]][0:10] if np.any(classes == ci) else 'nothing') for ci in
                    range(ek.num_classes)]
    plt.hist(classes, bins=range(ek.num_classes))
    plt.xticks(np.arange(ek.num_classes) + 0.5, class_labels, rotation='vertical')
    plt.title('Messages clusters')
    plt.show()
    pass
