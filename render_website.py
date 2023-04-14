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
        '-jp', '--json_path',
        help='in enter your path to the file',
        default=os.path.join(Path.cwd(), 'book_page.json')
    )
    args = parser.parse_args()
    return args


def on_reload(json_path, num_described_books_per_page):
    number_of_columns = 2
    Path('pages').mkdir(parents=True, exist_ok=True)
    with open(json_path, 'r') as file:
        book_descriptions = list(
            chunked(json.load(file), num_described_books_per_page)
        )
    total_pages_num = len(book_descriptions)
    for num, books_description_page in enumerate(book_descriptions, 1):
        description_books_page = chunked(
            books_description_page, number_of_columns
        )
        env = Environment(
            loader=FileSystemLoader('.'),
            autoescape=select_autoescape(['html'])
        )
        template = env.get_template(os.path.join('templates', 'template.html'))
        rendered_page = template.render(
            description_books_page=description_books_page,
            total_pages_num=total_pages_num,
            current_page_number=num,
        )
        with open(os.path.join(
                'pages', f'index{num}.html'
        ), 'w', encoding='utf8') as file:
            file.write(rendered_page)


def main():
    num_described_books_per_page = 10
    on_reload(gets_args().json_path, num_described_books_per_page)
    server = Server()
    server.watch(os.path.join('templates', 'template.html'), on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
