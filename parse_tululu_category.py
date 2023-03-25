from datetime import time
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import json
from requests import HTTPError
from manage import (check_for_redirect,
                    parse_book_page,
                    download_txt,
                    download_images
                    )


def main():
    for i in range(1, 1+1):
        try:
            response = requests.get(
                f"https://tululu.org/l55/{i}",
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
                print(page_tags)
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
