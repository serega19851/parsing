import argparse
import os
from pathlib import Path
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import json
from requests import HTTPError
from manage import (
    check_for_redirect,
    parse_book_page,
    download_txt,
    download_images,
)


def gets_last_number_page():
    url = "https://tululu.org/l55/"
    url_response = requests.get(url)
    url_response.raise_for_status()
    url_soup = BeautifulSoup(url_response.text, 'lxml')
    last_number_page = url_soup.select('.npage')[-1].text
    return last_number_page


def gets_args():
    parser = argparse.ArgumentParser('accepts optional args')
    parser.add_argument(
        "--start_page", type=int, help="enter the number", default=1
    )
    parser.add_argument(
        "--end_page",
        type=int,
        help="enter the number",
        default=gets_last_number_page()
    )
    parser.add_argument(
        "-si", "--skip_imgs",
        action="store_true",
        help="does not download"
    )
    parser.add_argument(
        "-df", "--dest_folder",
        help="in enter the path of the main directory",
        default='dest_folder'
    )

    parser.add_argument(
        "-st", "--skip_txt",
        action="store_true",
        help="does not download"
    )

    parser.add_argument(
        "-jp", "--json_path",
        help="in enter your path to the file",
        default=Path.cwd()
    )

    args = parser.parse_args()
    return args


def main():
    book_pages = []
    args = gets_args()
    for number in range(args.start_page, args.end_page + 1):
        try:
            response = requests.get(
                f"https://tululu.org/l55/{number}",
                allow_redirects=False
            )
            response.raise_for_status()
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            books_page = soup.select('.bookimage a')

            for book in books_page:
                try:
                    book_url = urljoin(response.url, book['href'])
                    book_response = requests.get(book_url)
                    book_response.raise_for_status()
                    check_for_redirect(book_response)
                    book_soup = BeautifulSoup(book_response.text, 'lxml')
                    book_page = parse_book_page(
                        book_soup,
                        book_url,
                    )
                    if not book_page['link']:
                        continue
                    book_download_link = urljoin(book_url, book_page['link'])
                    download_link_response = requests.get(
                        book_download_link, allow_redirects=False
                    )
                    download_link_response.raise_for_status()
                    check_for_redirect(download_link_response)
                    book_path = ''
                    img_path = ''
                    if not args.skip_txt:
                        book_path = download_txt(
                            download_link_response.content, book_page['title'],
                            args.dest_folder
                        )

                    if not args.skip_imgs:
                        img_path = download_images(
                            book_page['cover_book'],
                            args.dest_folder
                        )

                    page_book = {
                        "title": book_page['title'],
                        "author": book_page['author'],
                        "img_src": img_path,
                        "book_path": book_path,
                        "comments": book_page['comments'],
                        'genres': book_page['genres']
                    }
                    book_pages.extend([page_book])

                except HTTPError as inf:
                    print(
                        "Unable to download file",
                        book_response,
                        str(inf)
                    )

                except requests.exceptions.ConnectionError as errc:
                    print("Error Connecting:", errc)
                    time.sleep(5)

        except HTTPError as inf:
            print("Unable to download file", response.url, str(inf))

        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
            time.sleep(5)

    path_json = os.path.join(args.json_path, "book_page.json")
    with open(path_json, "w") as file:
        json.dump(
            book_pages,
            file,
            ensure_ascii=False,
            indent=4
        )


if __name__ == '__main__':
    main()
