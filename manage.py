from pprint import pprint
import requests
from pathlib import Path
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from requests import HTTPError
from urllib.parse import urlparse, urljoin
import argparse


def creates_directory(name):
    return Path(name).mkdir(parents=True, exist_ok=True)


def creates_new_urls(ranging):
    new_url = []
    for number in ranging:
        new_url.append(f"https://tululu.org/txt.php?id={number}")
    return new_url


def check_for_redirect(url, response):
    if url != response.url:
        raise HTTPError("Redirect detected. Download canceled")


def get_except(url):
    response = requests.get(url, allow_redirects=True)
    try:
        response.raise_for_status()
        check_for_redirect(url, response)
    except HTTPError as inf:
        print("Unable to download file ", url, str(inf))
        return ""
    return response.url


def gets_title(soup):
    title = soup.find('h1').text.split("::")
    return title[0].strip(), title[-1].strip()


def download_txt(url, filename, folder='books/'):
    creates_directory(folder)
    response = requests.get(url, allow_redirects=True)
    response.raise_for_status()
    path = f'{folder}{sanitize_filename(filename)}.txt'
    with open(path, 'wb') as file:
        file.write(response.content)
    return path


def display_link_cover_book(soup, book_url):
    book_cover = soup.find('div', class_='bookimage').find('img')['src']
    return urljoin(book_url, book_cover)


def download_images(soup, book_url, folder='images/'):
    creates_directory(folder)
    filename = urlparse(
        display_link_cover_book(soup, book_url)
    ).path.split("/")[-1]
    response = requests.get(display_link_cover_book(soup, book_url))
    response.raise_for_status()
    path = f'{folder}{sanitize_filename(filename)}'
    with open(path, 'wb') as file:
        file.write(response.content)


def gets_comments(soup):
    comments = soup.find_all('div', class_='texts')
    commentaries = []
    for comment in comments:
        commentaries.append(comment.find('span').text)
    return commentaries


def gets_book_genre(soup):
    genre = soup.find('span', class_='d_book').text.split(":")[-1].strip()
    return genre


def parse_book_page(soup, book_url, url):
    book_info = {
        'title': gets_title(soup)[0],
        'author': gets_title(soup)[1],
        'genre': gets_book_genre(soup),
        'comments': gets_comments(soup),
        'cover_book': display_link_cover_book(soup, book_url),
        'download_link': url,
    }
    pprint(book_info)


def create_parser():
    parser = argparse.ArgumentParser('accepts optional two numbers')
    parser.add_argument(
        "--start_id", type=int, help="enter the number", default=1
    )
    parser.add_argument(
        "--end_id", type=int, help="enter the number", default=5
    )
    args = parser.parse_args()
    ranging = range(args.start_id, args.end_id + 1)
    return ranging


def main():
    for url in creates_new_urls(create_parser()):
        if get_except(url):
            book_id = urlparse(url).query.split('=')[-1].strip()
            book_url = urljoin(url, f'b{book_id}/')
            response = requests.get(book_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            parse_book_page(soup, book_url, url)
            download_txt(url, gets_title(soup)[0])
            download_images(soup, book_url)


if __name__ == '__main__':
    main()
