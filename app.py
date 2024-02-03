from flask import Flask, request
import requests
import PyPDF2
import random
import io

app = Flask(__name__)
API_URL = "https://next.levity.ai/api/ai/v3/9278bba1-6cae-4108-8f4d-6037ad4ef4ba/classify"
HEADERS = {
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFtb2docHJhYmh1MTIzQGdtYWlsLmNvbSIsImxldml0eVVzZXJJZCI6IjBhYjI2ZjYyLTc0OGMtNDliMi1iZGU3LWNhOTk2ZGI3NzhkMCIsImxldml0eVdvcmtzcGFjZUlkIjoiOTVkYzgwM2YtNzgyNC00YjAyLTlmMzMtMmVlMThmZmI0ZjA2IiwiaXNzIjoiTGV2aXR5OjIifQ.GFYPrPeJNk5DrlCFGN7syKdLZxzEe7U4VQraXpwu--knApsR2InAzK0oJuVHmT6zae-xs3tfFbJejoIZswVwfoEKSH1CD4po0Nhx8eX1wkc2hUzGVsatP3dqG1qcHTcSohT0B8Ljwnvyw0gS6j4ibisv89tINaGGJZ1o91bnqiByQnkJ96oS8UIbmDyuQL7HDX_NE_AlBCOkRTmjKvlZIaw41UQq3WZu-wlRfsRgo5rbAMm3Tr-CKyBs-PvicD03HWlZP7LGZyE_losvVJ0dKSKfrP9HivmWHSQyu1b-p6TxaOzGNcNwzC3x1quA4rNflD_1q76KtS5nE2M4SfAd6A",
        "Content-Type": "application/json",
        "User-Agent": "Defined",
    }



def extract_text_from_pdf(url):
    response = requests.get(url)
    file = io.BytesIO(response.content)
    text = pdf_to_array(file)
    return text

def pdf_to_array(file):
    reader = PyPDF2.PdfReader(file)
    book = []

    # Add the first 2 pages
    book.append(reader.pages[0].extract_text())
    book.append(reader.pages[1].extract_text())

    # Extract random 100 pages
    page_nos = random.sample(range(2,len(reader.pages)),min(len(reader.pages)-2,200))
    for p in page_nos:
        book.append(reader.pages[p].extract_text())
    return book

def classify_text(text):
    book3 = text
    for i in range(len(book3)):
        words = book3[i].split(" ")
        word_count = len(words)
        one_letter_count = sum(len(word) == 1 for word in words)

        if one_letter_count / word_count > 0.8:
            # Do something
            pass
            book3[i] = "".join(words)

    for i in range(len(book3)):
        book3[i] = book3[i].replace("\n", " ")

    book = " ".join(book3)

    data = {
        "textToClassify": book if len(book) < 100000 else book[:100000]
    }

    response = requests.post(API_URL, headers=HEADERS, json=data)
    # response = {
    #     'labels': [
    #         {'value': 'Litrature', 'userValidated': 'not-rated'},
    #         {'value': 'English', 'userValidated': 'not-rated'}
    #     ],
    #     'text': 'The quick brown fox jumps over the lazy dog'
    # }

    return [label["value"] for label in response.json()["labels"]]

@app.route('/pdf-categories', methods=['POST'])
def get_pdf_categories():
    pdf_url = request.json['pdf_url']
    text = extract_text_from_pdf(pdf_url)
    categories = classify_text(text)
    return {'categories': categories}

if __name__ == '__main__':
    app.run(debug=True)
