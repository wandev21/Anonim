import re
import json


def get_categories(lines: list[str]) -> dict[str, list[str]]:
    cats = dict()
    for num, line in enumerate(lines):
        line = line.strip()
        if line.startswith('ТЕСТЫ ДЛЯ'):
            cat_name = line[19:-2]
            cats[cat_name] = []
            for inner_num, inner_line in enumerate(lines[num + 1:], start=1):
                if inner_line.startswith('ТЕСТЫ ДЛЯ'):
                    break
                cats[cat_name].append(inner_line)
    return cats


def parse_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = file.read()

    tests = []
    lines = data.splitlines(keepends=False)
    lines = [line for line in lines if line]

    cats = get_categories(lines)

    for key, val in cats.items():
        for num, line in enumerate(val):
            if line.startswith('Тест'):
                inner_tests = {
                    "cat": key,
                    "test_name": line[line.find('"')+1:-1],
                    "answers": []
                }
                for inner_num, inner_line in enumerate(val[num+1:]):
                    if inner_line == '-':
                        inner_tests['cover_url'] = None
                    elif inner_line.startswith('http'):
                        inner_tests['cover_url'] = inner_line
                    elif inner_line.startswith('Тест'):
                        break
                    elif bool(re.search(r'\d', inner_line[:3])):
                        answer = inner_line.split('.', maxsplit=1)[1].strip()
                        find_http = answer.rsplit(' ', maxsplit=1)
                        if len(find_http) == 2 and find_http[1].startswith('http'):
                            answer = find_http[0]
                            cover_url = find_http[1]
                        else:
                            cover_url = None
                        inner_tests['answers'].append(
                            {'text': answer, 'cover_url': cover_url}
                        )
                    else:
                        inner_tests['template'] = inner_line
                tests.append(inner_tests)
                print(inner_tests)
    return tests


if __name__ == '__main__':
    with open('new_data.json', 'w', encoding='utf-8') as f:
        json.dump(parse_file('catalogue.txt'), f, indent=4, ensure_ascii=False)
