# main.py
from flask import Flask, jsonify, request
from flask_cors import cross_origin
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import requests
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import timeout_decorator

app = Flask(__name__)


def driversetup():
    # The following options are required to make headless Chrome
    # work in a Docker container
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--window-size=1920,1080")
    # Initialize a new browser
    return webdriver.Chrome(options=chrome_options)


# @timeout_decorator.timeout(5)
def ExtractHTMLFromURL(url):
    # try using only requests
    try:
        html = requests.get(url).text
        return str(html)
    except:
        # first try using only requests
        driver = driversetup()
        driver.maximize_window()
        # navigate to browserstack.com
        driver.get(url)
        html = driver.page_source
        # close the browser
        driver.close()
        driver.quit()
        return str(html)


def extractTitleFromHTML(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string
    text = soup.get_text()
    return title, text


@app.route("/getTextForPDF", methods=["POST"])
@cross_origin(supports_credentials=True)
def getTextForPDF():
    data = request.json
    url = data["url"]
    try:
        response = requests.get(url)
        with open('tmp.pdf', 'wb') as file:
            file.write(response.content)
        with open('tmp.pdf', 'rb') as file:
            reader = PdfReader(file)
            pages = [(i, page.extract_text()) for i, page in enumerate(
                reader.pages) if page.extract_text() is not None]
            return jsonify({
                "pdfText": pages,
                "url": url,
            }), 200
    except:
        return jsonify({}), 400


@app.route("/getTextForURL", methods=["POST"])
@cross_origin(supports_credentials=True)
def getTextForURL():
    data = request.json
    url = data["url"]
    try:
        html = ExtractHTMLFromURL(url)
        title, text = extractTitleFromHTML(html)
        return jsonify({
            "text": text,
            "title": title,
            "url": url,
        }), 200
    except Exception as e:
        return jsonify({e}), 400
