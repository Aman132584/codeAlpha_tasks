
# Product FAQ Chatbot (NLP-based)

A chatbot that answers customer questions about a specific product or topic by matching user input against a set of FAQs using NLTK-based NLP techniques.

## How it works

1. Loads a list of product-related FAQ question-answer pairs
2. Preprocesses both stored questions and user input using NLTK (tokenization, lowercasing, stopword removal, lemmatization)
3. Compares the cleaned user question against all FAQ questions using similarity scoring (e.g. TF-IDF + cosine similarity)
4. Returns the answer tied to the closest matching FAQ
5. Falls back to a default "I'm not sure, please contact support" response if similarity is too low

## Setup

```
pip install nltk scikit-learn
```

On first run, download the required NLTK data:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
```

`faqs.json` holds your product's question-answer pairs, e.g.:

```json
[
  { "question": "What is the warranty period for this product?", "answer": "The product comes with a 1-year warranty." },
  { "question": "How do I track my order?", "answer": "Use the tracking link sent to your email after purchase." }
]
```

## Usage

```
python chatbot.py
```

Type a question about the product and the bot replies with the closest matching answer. Type `exit` to quit.

## Notes

- Add more Q&A pairs to `faqs.json` to widen topic coverage
- Similarity threshold can be tuned in the code to control how strict matching is
- Works fully offline once NLTK data is downloaded — no external API needed
- For better accuracy on paraphrased questions, consider swapping TF-IDF for sentence embeddings later
