from flask import Flask
import crawling
app = Flask(__name__)

@app.route('/')
def index():
    driver = crawling.initialize_driver()
    crawling.login_hogangnono(driver)
    crawling.search_apartment_review(driver, "반포동 반포자이")
    review_json = crawling.crawling_review(driver)
    return review_json

app.run(debug=True)