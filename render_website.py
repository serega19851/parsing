import json
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    with open("book_page.json", "r") as file:
        book_page = file.read()
    book_pages = chunked(json.loads(book_page), 2)
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )

    template = env.get_template(os.path.join('templates', "index.html"))
    rendered_page = template.render(book_pages=book_pages)

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch('templates/index.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
