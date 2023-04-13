import argparse
import json
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def gets_args():
    parser = argparse.ArgumentParser('accepts optional args')
    parser.add_argument(
        "-jp", "--json_path",
        help="in enter your path to the file",
        default=Path.cwd()
    )
    args = parser.parse_args()
    return args


def on_reload(json_path):
    Path('pages').mkdir(parents=True, exist_ok=True)
    path_json = os.path.join(json_path, "book_page.json")
    with open(path_json, "r") as file:
        book_descriptions = list(chunked(json.load(file), 10))
    pages_number = len(book_descriptions)
    for num, page_with_books in enumerate(book_descriptions, 1):
        books_part = chunked(page_with_books, 2)
        env = Environment(
            loader=FileSystemLoader('.'),
            autoescape=select_autoescape(['html'])
        )
        template = env.get_template(os.path.join('templates', "template.html"))
        rendered_page = template.render(
            books_part=books_part,
            pages_number=pages_number,
            current_page=num,
        )
        with open(os.path.join(
                'pages', f'index{num}.html'
        ), 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    on_reload(gets_args().json_path)
    server = Server()
    server.watch(os.path.join('templates', 'template.html'), on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
