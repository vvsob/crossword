import random
import json

letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

with open("words.json", 'rb') as fin:
    word_data = json.load(fin)
    word_data = {word: meaning for word, meaning in word_data.items() if all(map(lambda c: c in letters, word))}
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

        if vertical_left == 0 and horizontal_left == 0:
            # print(vertical_generated, horizontal_generated)
            return vertical_generated, horizontal_generated

        # if vertical_left <= 2 or horizontal_left <= 2:
        #     print(vertical_left, horizontal_left)

        # vertical words
        for i in range(self.horizontal):
            if vertical_generated[i]:
                vertical_candidates[i] = []
                continue
            vertical_candidates[i] = list(filter(lambda w: self.check(w, 'vertical', i, vertical_generated, horizontal_generated), vertical_candidates[i]))
            if self.use_sort:
                vertical_candidates[i].sort(key=lambda w: self.rate(w, 'vertical', i), reverse=True)
            if not vertical_candidates[i]:
                return None

        # horizontal words
        for i in range(self.vertical):
            if horizontal_generated[i]:
                horizontal_candidates[i] = []
                continue
            horizontal_candidates[i] = list(filter(lambda w: self.check(w, 'horizontal', i, vertical_generated, horizontal_generated), horizontal_candidates[i]))
            if self.use_sort:
                horizontal_candidates[i].sort(key=lambda w: self.rate(w, 'horizontal', i), reverse=True)
            if not horizontal_candidates[i]:
                return None

        min_vertical = -1
        for i, el in enumerate(vertical_candidates):
            if vertical_generated[i]:
                continue
            if min_vertical == -1 or len(el) < len(vertical_candidates[min_vertical]):
                min_vertical = i

        min_horizontal = -1
        for i, el in enumerate(horizontal_candidates):
            if horizontal_generated[i]:
                continue
            if min_horizontal == -1 or len(el) < len(horizontal_candidates[min_horizontal]):
                min_horizontal = i

        if min_horizontal == -1 or (min_vertical != -1 and len(vertical_candidates[min_vertical]) < len(horizontal_candidates[min_horizontal])):
            for word in vertical_candidates[min_vertical]:
                vertical_generated[min_vertical] = word
                result = self.generate(vertical_left - 1, horizontal_left, vertical_generated.copy(), horizontal_generated.copy(), vertical_candidates.copy(), horizontal_candidates.copy())
                if result:
                    return result
        else:
            for word in horizontal_candidates[min_horizontal]:
                horizontal_generated[min_horizontal] = word
                result = self.generate(vertical_left, horizontal_left - 1, vertical_generated.copy(), horizontal_generated.copy(), vertical_candidates.copy(), horizontal_candidates.copy())
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

        vertical_result, horizontal_result = self.generate(self.horizontal, self.vertical, vertical_generated, horizontal_generated, vertical_candidates, horizontal_candidates)
        vertical_meanings = list(map(lambda w: word_data[w]['definition'], vertical_result))
        horizontal_meanings = list(map(lambda w: word_data[w]['definition'], horizontal_result))
        return '\n'.join(horizontal_result), (vertical_meanings, horizontal_meanings)

    def __init__(self, vertical, horizontal, use_sort=False):
        self.vertical = vertical
        self.horizontal = horizontal
        self.use_sort = use_sort

        self.vertical_words = list(filter(lambda s: len(s) == vertical and '-' not in s, all_words))
        self.horizontal_words = list(filter(lambda s: len(s) == horizontal and '-' not in s, all_words))

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


def make(width, height):
    gen = Generator(height, width)
    return gen.make()


def main():
    for w in range(3, 7):
        for h in range(w, 7):
            print(f'==== {w}x{h}')
            words, (vertical_definitions, horizontal_definitions) = make(w, h)
            print(words)
            print()
            print('По горизонтали:')
            print('\n'.join(map(lambda pair: f"{pair[0] + 1}: {pair[1]}", enumerate(horizontal_definitions))))
            print()
            print('По вертикали:')
            print('\n'.join(map(lambda pair: f"{pair[0] + 1}: {pair[1]}", enumerate(vertical_definitions))))
            print()
            print()


if __name__ == '__main__':
    main()
