import time
import requests
from pathlib import Path
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from requests import HTTPError
from urllib.parse import urljoin
import argparse
import os


def check_for_redirect(response):
    if response.is_redirect:
        raise HTTPError("Redirect detected. Download canceled")


def gets_title(soup):
    title, author = soup.select_one('h1').text.split('::')
    return title.strip(), author.strip()


def download_txt(
        response_content,
        filename,
        dest_folder='dest_folder',
        folder='books'
):
    Path(
        os.path.join(dest_folder, folder)
    ).mkdir(parents=True, exist_ok=True)

    path = os.path.join(
        dest_folder,
        folder,
        f'{sanitize_filename(filename)}.txt'
    )
    with open(path, 'wb') as file:
        file.write(response_content)
    return path


def get_url_cover_book(soup, book_url):
    book_cover = soup.select_one('.bookimage img')['src']
    return urljoin(book_url, book_cover)


def download_images(
        url_cover,
        dest_folder='dest_folder',
        folder='images'
):
    Path(
        os.path.join(dest_folder, folder)
    ).mkdir(parents=True, exist_ok=True)

    filename = url_cover.split('/')[-1]
    response = requests.get(url_cover)
    response.raise_for_status()
    path = os.path.join(
        dest_folder,
        folder,
        sanitize_filename(filename)
    )
    with open(path, 'wb') as file:
        file.write(response.content)
    return path


def gets_comments(soup):
    comments = soup.select('.texts span')
    commentaries = [comment.text for comment in comments]
    return commentaries


def gets_book_genres(soup):
    genres = soup.select_one('span.d_book').text.split(":")[-1].strip()
    return genres


def parse_book_page(soup, book_url):
    title, author = gets_title(soup)
    tag = soup.select_one('.d_book a[href^="/txt.php"]')
    link = ''
    if tag:
        link = tag['href']
    book_page = {
        'title': title,
        'author': author,
        'genres': gets_book_genres(soup),
        'comments': gets_comments(soup),
        'cover_book': get_url_cover_book(soup, book_url),
        'link': link
    }
    return book_page


def gets_number_args():
    parser = argparse.ArgumentParser('accepts optional two numbers')
    parser.add_argument(
        "--start_id", type=int, help="enter the number", default=1
    )
    parser.add_argument(
        "--end_id", type=int, help="enter the number", default=5
    )
    args = parser.parse_args()
    return args.start_id, args.end_id


def main():
    start_id, end_id = gets_number_args()
    for number in range(start_id, end_id + 1):
        try:
            params = {'id': number}
            response = requests.get(
                "https://tululu.org/txt.php",
                params=params,
                allow_redirects=False
            )
            response.raise_for_status()
            book_url = urljoin(response.url, f'b{number}/')

            book_response = requests.get(book_url)
            book_response.raise_for_status()
            soup = BeautifulSoup(book_response.text, 'lxml')

            check_for_redirect(response)
            check_for_redirect(book_response)
            book_page = parse_book_page(
                soup,
                book_url,
            )
            download_images(book_page['cover_book'])
            download_txt(response.content, book_page['title'])
        except HTTPError as inf:
            print("Unable to download file ", response.url, str(inf))

        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
            time.sleep(5)


if __name__ == '__main__':
    main()
