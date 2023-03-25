import argparse
from datetime import time
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import json
from requests import HTTPError
from manage import (check_for_redirect,
                    parse_book_page,
                    download_txt,
                    download_images,
                    )


def get_last_number_pages():
    url = "https://tululu.org/l55/"
    url_response = requests.get(url)
    url_response.raise_for_status()
    url_soup = BeautifulSoup(url_response.text, 'lxml')
    last_number_page = url_soup.select('.npage')[-1].text
    return last_number_page


def gets_number_page_args():
    parser = argparse.ArgumentParser('accepts optional two numbers')
    parser.add_argument(
        "--start_page", type=int, help="enter the number", default=1
    )
    parser.add_argument(
        "--end_page",
        type=int,
        help="enter the number",
        default=get_last_number_pages()
    )
    args = parser.parse_args()
    return args.start_page, args.end_page


def main():
    start_page, end_page = gets_number_page_args()
    for number in range(start_page, end_page + 1):
        try:
            response = requests.get(
                f"https://tululu.org/l55/{number}",
                allow_redirects=False
            )
            response.raise_for_status()
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            books_page = soup.select('.bookimage a')

            book_pages = []
            for book in books_page:
                book_url = urljoin(response.url, book['href'])
                book_response = requests.get(book_url)
                book_response.raise_for_status()
                check_for_redirect(book_response)
                book_soup = BeautifulSoup(book_response.text, 'lxml')
                page_tags = book_soup.select('.d_book a ')
                link = [
                    tag['href'] for tag in page_tags if 'txt' in tag['href']
                ]

                book_page = parse_book_page(
                    book_soup,
                    book_url,
                )

                if link:
                    book_download_link = urljoin(book_url, str(*link))
                    download_link_response = requests.get(
                        book_download_link, allow_redirects=False
                    )
                    download_link_response.raise_for_status()
                    check_for_redirect(download_link_response)
                    path = download_txt(
                        download_link_response.content, book_page['title']
                    )

                    download_images(book_page['cover_book'])
                    page_book = {
                        "title": book_page['title'],
                        "author": book_page['author'],
                        "img_src": urlparse(book_page['cover_book']).path,
                        "book_path": path,
                        "comments": book_page['comments'],
                        'genres': book_page['genres']
                          }
                    book_pages.extend([page_book])

            book_page_json = json.dumps(
                book_pages,
                ensure_ascii=False,
                indent=4
            )
            with open("book_page.json", "w") as my_file:
                my_file.write(book_page_json)

        except HTTPError as inf:
            print("Unable to download file ", response.url, str(inf))
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
            time.sleep(5)


if __name__ == '__main__':
    main()
