import random
import json

def is_int(data):
    try:
        int(data)
        return True
    except ValueError:
        return False

def generate_poem():
    with open('config/dict.json', 'r', encoding='utf-8') as dict_file:
        vocabular = json.load(dict_file)

    random_values = []

    for i in range(len(vocabular)):
        random_values.append(random.choice(vocabular[i]))

    with open('config/structure.json', 'r', encoding='utf-8') as structure_file:
        structure = json.load(structure_file)

    poem = []

    for i in range(len(structure)):
        element = ""
        for j in range(len(structure[i])):
            if is_int(structure[i][j]):
                element += random_values[structure[i][j]] + " "
            else:
                element += structure[i][j] + " "
        poem.append(element.rstrip())  # Удаление лишних пробелов в конце строки

    return poem

if __name__ == "__main__":
    poem = generate_poem()
    for line in poem:
        print(line)
