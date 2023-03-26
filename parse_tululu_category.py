import argparse
import os
from pathlib import Path
from datetime import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import json
from requests import HTTPError
from manage import (check_for_redirect,
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
        action="store_true",
        help="show directory paths"
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
    for number in range(gets_args().start_page, gets_args().end_page + 1):
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
                    if not gets_args().skip_txt:
                        book_path = download_txt(
                            download_link_response.content, book_page['title']
                        )
                    else:
                        book_path = "didn't download"
                    if not gets_args().skip_imgs:
                        img_path = download_images(book_page['cover_book'])
                    else:
                        img_path = "didn't download"

                    page_book = {
                        "title": book_page['title'],
                        "author": book_page['author'],
                        "img_src": img_path,
                        "book_path": book_path,
                        "comments": book_page['comments'],
                        'genres': book_page['genres']
                        }
                    book_pages.extend([page_book])

            book_page_json = json.dumps(
                book_pages,
                ensure_ascii=False,
                indent=4
            )
            path_json = os.path.join(gets_args().json_path, "book_page.json")
            with open(path_json, "w") as my_file:
                my_file.write(book_page_json)

        except HTTPError as inf:
            print("Unable to download file", response.url, str(inf))

        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
            time.sleep(5)

    if gets_args().dest_folder:
        print(path_json)
        if not gets_args().skip_txt:
            print(
                Path(
                    os.path.join(
                        gets_args().json_path, book_pages[0]['book_path']
                    )
                ).parent
            )
        else:
            print("didn't download")
        if not gets_args().skip_imgs:
            print(
                Path(
                    os.path.join(
                        gets_args().json_path, book_pages[0]['img_src']
                    )
                ).parent
            )
        else:
            print("didn't download")


if __name__ == '__main__':
    main()
