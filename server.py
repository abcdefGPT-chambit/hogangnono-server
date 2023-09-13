from flask import Flask, request  # request 추가
import crawling
import concurrent.futures
import json

app = Flask(__name__)

@app.route('/crawl')
def index():
    url = request.args.get('url')  # URL 매개변수에서 URL을 가져옴
    driver = crawling.initialize_driver()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        review_list = executor.submit(crawling.crawling_review, driver, url).result()

    review_json = json.dumps(review_list, ensure_ascii=False, indent=4)

    return review_json

if __name__ == '__main__':
    app.run()