from pprint import pprint

from bot_operations.bot_support.keyboards import create_links_keyboard

def test1():
    links = ['abc','def']
    awa = create_links_keyboard(links, 2)
    pprint(awa.inline_keyboard)

def test2():
    def split_by_size(seq, row_width=3):
        return [seq[i:i + row_width] for i in range(0, len(seq), row_width)]

    # Пример:
    lst = [1]
    print(split_by_size(lst))  # [[1,2,3],[4,5,6],[7]]

def test3():
    print(int(1/2))

if __name__ == '__main__':
    test2()