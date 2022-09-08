import re
from random import choice
import sys
import dill
import os
import collections


class TextGenerator:
    def __init__(self, length_of_gram):
        self.dict_of_words = collections.defaultdict(list)
        self.length_of_gram = length_of_gram

    @staticmethod
    def tokenize(text):  # токенизация текста, чтобы оставить только слова в нижнем регистре
        return re.findall(r'(?:[а-яё]+\-[а-яё]+)|[а-яё]+', text.lower())

    @staticmethod
    def file_reader(input_dir):  # считываем все файлы из директории и делаем список с текстами оттуда
        lst_of_text = []
        if input_dir == 'stdin':
            lst_of_text.append(sys.stdin.readlines())
        else:
            ls = os.listdir(input_dir)
            for elem in ls:
                with open(input_dir + '/' + elem, 'r', encoding='utf-8') as file_in:
                    lst_of_text.append(file_in.read())
        return lst_of_text

    @staticmethod
    def merge_defaultdicts(d1, d2):  # слияние двух defauldict в d2
        for k, v in d1.items():
            d2[k].extend(v)
        return d2

    def fit(self, model, input_dir='stdin'):
        lst_of_text = self.file_reader(input_dir)
        for elem in lst_of_text:  # будем делать для каждого файла в директории свой словарь
            dict_of_words = collections.defaultdict(list)
            filter_words = self.tokenize(elem)
            filter_words.extend((filter_words[:self.length_of_gram:]))
            # добавим в конец этого списка из начала количество слов, равное размену одного префикса, чтобы для каждого префикса можно было его чем-то продолжить
            for i in range(len(filter_words) - self.length_of_gram):
                prefix = tuple(filter_words[i:(i + self.length_of_gram):])
                if len(prefix) == self.length_of_gram:  # чтобы добавлять только префиксы необходимой длины
                    dict_of_words[prefix].append(filter_words[i + self.length_of_gram])
            self.merge_defaultdicts(dict_of_words, self.dict_of_words)  # объединим словари в один
        with open(model, 'wb') as file_out:  # сохранение экземпляра класса в файл с помощью dill
            dill.dump(self, file_out)

    def generate(self, length, prefix=''):
        dict_of_words = self.dict_of_words
        new_prefix_lst = []
        if prefix != '':
            prefix_lst = self.tokenize(prefix)
            if len(prefix_lst) >= self.length_of_gram:
                new_prefix_lst = prefix_lst[:self.length_of_gram]
                # если заданный префикс больше чем нужно, возьмем только часть, равную размеру n-граммы
            elif len(prefix_lst) < self.length_of_gram:
                lst = list(filter(lambda x: x[:len(prefix_lst)] == tuple(prefix_lst), dict_of_words.keys()))
                if lst:
                    new_prefix_lst = list(choice(lst))
                # если заданный префикс меньше, чем нужно, дополним его случайными словами, до размера n-граммы
            if tuple(new_prefix_lst) not in dict_of_words:
                raise ValueError('Префикса нет в тексте')
            ans = new_prefix_lst.copy()  # записываем заданный префикс в ответ
            ans.append((choice(dict_of_words[tuple(ans)])))
            # добавляем следующее слово, чтобы далее двигаться по префиксам нужной длины
            start = len(new_prefix_lst) - self.length_of_gram + 1
            # чтобы начинать не с начала, а с того места сколько мы добавили по заданному префиксу
        else:
            ans = list(choice(list(dict_of_words)))  # случайно выбираем начальный префикс, если его не передали
            start = 0
        for i in range(start, length - self.length_of_gram):
            ans.append(choice(
                dict_of_words[tuple(ans[i:i + self.length_of_gram])]))  # по каждому префиксу выбираем случайное слово
        print(' '.join(ans))


model_1 = TextGenerator(length_of_gram=3)
model_1.fit(model='models/model', input_dir='data')
