import random
import json
import time
import multiprocessing

letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

with open("words.json", 'rb') as fin:
    word_data = json.load(fin)
    word_data = {word: meaning for word, meaning in word_data.items() if
                 all(map(lambda c: c in letters, word))}
    all_words = list(word_data.keys())


class Generator:
    def rate(self, word, orientation, index):
        res = 1
        occurrences = self.horizontal_occurrences
        if orientation == 'horizontal':
            occurrences = self.vertical_occurrences

        for c in word:
            res *= occurrences[index][c]

        return res

    def check(self, word, orientation, i,
              vertical_generated, horizontal_generated):
        if word in vertical_generated or word in horizontal_generated:
            return False

        if orientation == 'vertical':
            for j, h_word in enumerate(horizontal_generated):
                if h_word is None:
                    continue
                if word[j] != h_word[i]:
                    return False
        else:
            for j, v_word in enumerate(vertical_generated):
                if v_word is None:
                    continue
                if word[j] != v_word[i]:
                    return False
        return True

    def generate(self,
                 vertical_left, horizontal_left,
                 vertical_generated, horizontal_generated,
                 vertical_candidates, horizontal_candidates):

        # if vertical_left + horizontal_left == 11:
        #     print(vertical_generated, horizontal_generated)

        if vertical_left + horizontal_left <= self.max_error:
            # print(vertical_generated, horizontal_generated)
            return vertical_generated, horizontal_generated

        # if vertical_left <= 2 or horizontal_left <= 2:
        #     print(vertical_left, horizontal_left)

        # vertical words
        for i in range(self.horizontal):
            if vertical_generated[i]:
                vertical_candidates[i] = []
                continue
            vertical_candidates[i] = list(filter(
                lambda w: self.check(w, 'vertical', i, vertical_generated, horizontal_generated),
                vertical_candidates[i]))
            if self.use_sort:
                vertical_candidates[i].sort(key=lambda w: self.rate(w, 'vertical', i), reverse=True)
            # for word in vertical_candidates[i]:
            #     vertical_generated[i] = word
            #     result = self.generate(vertical_left - 1, horizontal_left,
            #                            vertical_generated.copy(), horizontal_generated.copy(),
            #                            vertical_candidates.copy(), horizontal_candidates.copy())
            #     if result:
            #         return result
            # vertical_generated[i] = None
            if not vertical_candidates[i]:
                return None

        # horizontal words
        for i in range(self.vertical):
            if horizontal_generated[i]:
                horizontal_candidates[i] = []
                continue
            horizontal_candidates[i] = list(filter(
                lambda w: self.check(w, 'horizontal', i, vertical_generated, horizontal_generated),
                horizontal_candidates[i]))
            if self.use_sort:
                horizontal_candidates[i].sort(key=lambda w: self.rate(w, 'horizontal', i),
                                              reverse=True)
            # for word in horizontal_candidates[i]:
            #     horizontal_generated[i] = word
            #     result = self.generate(vertical_left, horizontal_left - 1,
            #                            vertical_generated.copy(), horizontal_generated.copy(),
            #                            vertical_candidates.copy(), horizontal_candidates.copy())
            #     if result:
            #         return result
            # horizontal_generated[i] = None
            if not horizontal_candidates[i]:
                return None

        sel_vertical = -1
        for i, el in enumerate(vertical_candidates):
            if vertical_generated[i]:
                continue
            if sel_vertical == -1 or len(el) < len(vertical_candidates[sel_vertical]):
                sel_vertical = i

        sel_horizontal = -1
        for i, el in enumerate(horizontal_candidates):
            if horizontal_generated[i]:
                continue
            if sel_horizontal == -1 or len(el) < len(horizontal_candidates[sel_horizontal]):
                sel_horizontal = i

        if sel_horizontal == -1 or (
                sel_vertical != -1 and len(vertical_candidates[sel_vertical]) < len(
                horizontal_candidates[sel_horizontal])):
            for word in vertical_candidates[sel_vertical]:
                vertical_generated[sel_vertical] = word
                result = self.generate(vertical_left - 1, horizontal_left,
                                       vertical_generated.copy(), horizontal_generated.copy(),
                                       vertical_candidates.copy(), horizontal_candidates.copy())
                if result:
                    return result
        else:
            for word in horizontal_candidates[sel_horizontal]:
                horizontal_generated[sel_horizontal] = word
                result = self.generate(vertical_left, horizontal_left - 1,
                                       vertical_generated.copy(), horizontal_generated.copy(),
                                       vertical_candidates.copy(), horizontal_candidates.copy())
                if result:
                    return result

    def make(self):
        vertical_generated = [None] * self.horizontal
        horizontal_generated = [None] * self.vertical

        vertical_candidates = [self.vertical_words.copy() for _ in range(self.horizontal)]
        if self.use_sort:
            for i, row in enumerate(vertical_candidates):
                row.sort(key=lambda w: self.rate(w, 'vertical', i), reverse=True)

        horizontal_candidates = [self.horizontal_words.copy() for _ in range(self.vertical)]
        if self.use_sort:
            for i, row in enumerate(horizontal_candidates):
                row.sort(key=lambda w: self.rate(w, 'horizontal', i), reverse=True)

        vertical_result, horizontal_result = self.generate(self.horizontal, self.vertical,
                                                           vertical_generated, horizontal_generated,
                                                           vertical_candidates,
                                                           horizontal_candidates)

        vertical_meanings = list(map(lambda w: '' if not w else word_data[w]['definition'], vertical_result))
        horizontal_meanings = list(map(lambda w: '' if not w else word_data[w]['definition'], horizontal_result))

        res_matrix = [['#' for j in range(self.horizontal)] for i in range(self.vertical)]
        for j, w in enumerate(vertical_result):
            if w:
                for i, c in enumerate(w):
                    res_matrix[i][j] = c

        for i, w in enumerate(horizontal_result):
            if w:
                for j, c in enumerate(w):
                    res_matrix[i][j] = c

        return '\n'.join(map(''.join, res_matrix)), (vertical_meanings, horizontal_meanings)

    def __init__(self, vertical, horizontal, use_sort=False, max_error=0):
        self.vertical = vertical
        self.horizontal = horizontal
        self.use_sort = use_sort
        self.max_error = max_error

        self.vertical_words = list(filter(lambda s: len(s) == vertical and '-' not in s, all_words))
        self.horizontal_words = list(
            filter(lambda s: len(s) == horizontal and '-' not in s, all_words))

        self.vertical_occurrences = [dict.fromkeys(letters, 0) for _ in range(vertical)]
        for w in self.vertical_words:
            for i, c in enumerate(w):
                self.vertical_occurrences[i][c] += 1

        self.horizontal_occurrences = [dict.fromkeys(letters, 0) for _ in range(horizontal)]
        for w in self.horizontal_words:
            for i, c in enumerate(w):
                self.horizontal_occurrences[i][c] += 1

        random.shuffle(self.vertical_words)
        random.shuffle(self.horizontal_words)


def make(width, height, max_error=0):
    gen = Generator(height, width, max_error=max_error)
    return gen.make()


def transpose(matrix):
    matrix = matrix.split('\n')
    res = [''.join([matrix[j][i] for j in range(len(matrix))]) for i in range(len(matrix[0]))]
    return '\n'.join(res)


class ThreadedGenerator:
    @staticmethod
    def do_thread(th_index, w, h, max_error, start_event, new_event, queue):
        start_event.wait()
        while True:
            words = ''
            start = time.time()
            words, _ = make(w, h, max_error)
            stop = time.time()
            queue.put({'words': words, 'th_index': th_index, 'time': stop - start})
            new_event.set()

    def start(self):
        log_file = open('results/crossword_list.txt', mode='w', encoding='utf-8')

        return_queue = multiprocessing.Queue()
        self.threads = [multiprocessing.Process(target=ThreadedGenerator.do_thread,
                                                args=(i, self.w, self.h, self.max_error,
                                                      self.start_event, self.new_result_event,
                                                      return_queue))
                        for i in range(self.threads_count)]

        for th in self.threads:
            th.start()
        self.start_event.set()
        print('Начата генерация')

        index = 0
        while True:
            self.new_result_event.wait()
            self.new_result_event.clear()
            index += 1
            new_crossword = {'words': '', 'th_index': -1, 'time': 0}
            while new_crossword == {'words': '', 'th_index': -1, 'time': 0} \
                    or new_crossword['words'] in self.results_seen:
                new_crossword = return_queue.get()

            print(f"==== Кроссворд №{index}")
            print(new_crossword['words'])
            print(f"Выполнил процесс №{new_crossword['th_index']}")
            print(f"Затраченное время: {round(new_crossword['time'], 5)} секунд")

            log_file.write(f"{new_crossword['words']}\n{new_crossword['th_index']}\n{new_crossword['time']}\n\n")

            self.results_seen.add(new_crossword['words'])
            self.results_seen.add(transpose(new_crossword['words']))

    def __init__(self, w, h, max_error=0, threads_count=1):
        self.w = w
        self.h = h
        self.max_error = max_error
        self.threads_count = threads_count
        self.threads = list()
        self.start_event = multiprocessing.Event()
        self.new_result_event = multiprocessing.Event()
        self.results_seen = set()


def main():
    gen = ThreadedGenerator(7, 7, max_error=6, threads_count=6)
    gen.start()


    # seen = set()
    # for i in range(1000):
    #     words = ''
    #     print(f'=== Кроссворд №{i + 1}:')
    #     start = time.time()
    #     attempts = 0
    #     while words == '' or words in seen:
    #         attempts += 1
    #         words, _ = make(5, 5)
    #     end = time.time()
    #     print(words)
    #     print(f"Затраченное время: {round(end - start, 3)} секунд")
    #     print(f"Количество попыток: {attempts}")
    #     seen.add(words)

    # for w in range(3, 7):
    #     for h in range(w, 7):
    #         print(f'==== {w}x{h}')
    #         words, (vertical_definitions, horizontal_definitions) = (w, h)
    #         print(words)
    #         print()
    #         print('По горизонтали:')
    #         print('\n'.join(
    #             map(lambda pair: f"{pair[0] + 1}: {pair[1]}", enumerate(horizontal_definitions))))
    #         print()
    #         print('По вертикали:')
    #         print('\n'.join(
    #             map(lambda pair: f"{pair[0] + 1}: {pair[1]}", enumerate(vertical_definitions))))
    #         print()
    #         print()


if __name__ == '__main__':
    main()
