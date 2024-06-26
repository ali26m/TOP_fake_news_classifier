import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import contractions
from nltk.stem import WordNetLemmatizer
import pickle
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

app = FastAPI(
    title="TOP API",
    docs_url="docs", 
    description="TOP API tackles the challenge of fake news detection using artificial intelligence. Its core functionality lies in analyzing text and classifying it as real or fake news. This is achieved through a machine learning model trained on a massive dataset of labeled news articles. The model, a decision tree, works by dissecting the text and identifying patterns that differentiate real news from fabricated stories."
)

class article(BaseModel):
    text: str

vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
transformer = pickle.load(open('transformer.pkl', 'rb'))
model = pickle.load(open('dt.pkl', 'rb'))

@app.get("/", tags=["Health check"])
def root():
    return {"Health": "200 OK"}

@app.post("/classify", tags=["Classify a news article"])
def classify(input: article):
    
    text = re.sub(r'http\S+', '', str(input.text))
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'<.*>', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    words = word_tokenize(text)
    english_stopwords = set(stopwords.words('english'))
    filtered_words = []
    for word in words:
        if word.lower() not in english_stopwords:
            filtered_words.append(word)
    text = ' '.join(filtered_words)
    text = text.lower()
    text = contractions.fix(text)
    text_tokenized = []
    words = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    for word in words:
        text_tokenized.append(lemmatizer.lemmatize(word))
    text = ' '.join(text_tokenized)
    text = [text]

    counts = vectorizer.transform(text)
    tfidf = transformer.transform(counts)

    prediction = model.predict(tfidf)

    return {"prediction": str(prediction[0])}

    # uvicorn topapi:app --reload