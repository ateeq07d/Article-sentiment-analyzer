from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob

app = Flask(__name__)

def analyze_article(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get title
    title = soup.find('h1').get_text() if soup.find('h1') else "No Title"

    # Get paragraphs
    paragraphs = [p.get_text() for p in soup.find_all('p')]

    # Short and full text
    short_desc = " ".join(paragraphs[:3])
    full_text = " ".join(paragraphs)

    # Sentiment analysis
    blob = TextBlob(full_text)
    sentences = blob.sentences

    pos = neg = neu = 0

    for s in sentences:
        polarity = s.sentiment.polarity
        if polarity > 0:
            pos += 1
        elif polarity < 0:
            neg += 1
        else:
            neu += 1

    total = pos + neg + neu if (pos + neg + neu) != 0 else 1

    pos_per = round((pos / total) * 100, 2)
    neg_per = round((neg / total) * 100, 2)
    neu_per = round((neu / total) * 100, 2)

    # ⭐ Rating logic (1–5)
    if pos_per > neg_per:
        rating = 4
        if pos_per > 70:
            rating = 5
    elif neg_per > pos_per:
        rating = 2
        if neg_per > 70:
            rating = 1
    else:
        rating = 3

    return {
        "title": title,
        "short": short_desc,
        "full": full_text,
        "pos": pos_per,
        "neg": neg_per,
        "neu": neu_per,
        "rating": rating
    }

@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    if request.method == "POST":
        url = request.form["url"]
        data = analyze_article(url)

    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)