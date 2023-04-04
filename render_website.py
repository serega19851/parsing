import json
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    Path('pages').mkdir(parents=True, exist_ok=True)
    with open("book_page.json", "r") as file:
        books = file.read()
    book_pages = chunked(json.loads(books), 20)

    for num, page in enumerate(book_pages):
        books_part = chunked(page, 2)

        env = Environment(
            loader=FileSystemLoader('.'),
            autoescape=select_autoescape(['html'])
        )
        template = env.get_template(os.path.join('templates', "index.html"))
        rendered_page = template.render(books_part=books_part)
        with open(os.path.join(
                'pages', f'index{num + 1}.html'
        ), 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch(os.path.join('templates', 'index.html'), on_reload)
    server.serve(root='./pages/index1.html')


if __name__ == '__main__':
    main()
