import pandas as pd
import nltk
import string
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify
from flask_cors import CORS


nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

def load_file(filepath):
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Could not find {filepath}")
        return None


def preprocess_text(text):
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    words = word_tokenize(text.lower())

    cleaned = [
        lemmatizer.lemmatize(word)
        for word in words
        if word not in stop_words and word not in string.punctuation
    ]

    return ' '.join(cleaned)


def match_question(user_question):
    cleaned_q = preprocess_text(user_question)
    query_vector = vectorizer.transform([cleaned_q])
    scores = cosine_similarity(query_vector, faq_vectors)

    best_index = scores.argmax()
    best_score = scores[0][best_index]

    if best_score < THRESHOLD:
        return None, None, best_score

    answer = df.iloc[best_index]['Answer']
    matched = df.iloc[best_index]['Question']

    return answer, matched, round(float(best_score), 2)


df = load_file('faqs.csv')
df['cleaned'] = df['Question'].apply(preprocess_text)

vectorizer = TfidfVectorizer()
faq_vectors = vectorizer.fit_transform(df['cleaned'])

THRESHOLD = 0.2

app = Flask(__name__)
CORS(app)


@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.get_json()

    if not data or 'question' not in data:
        return jsonify({'error': 'Missing question field'}), 400

    user_question = data['question'].strip()

    if not user_question:
        return jsonify({'error': 'Question is empty'}), 400

    answer, matched, score = match_question(user_question)

    if answer is None:
        return jsonify({'answer': None})

    return jsonify({
        'answer': answer,
        'matched_question': matched,
        'score': score
    })
if __name__ == '__main__':
    print(f"Loaded {len(df)} FAQs successfully")
    print("Running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)