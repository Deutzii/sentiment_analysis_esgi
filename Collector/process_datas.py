import csv
import os
import glob
import pandas as pd
import numpy as np
import time
import nltk
from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM, SpatialDropout1D
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
from keras.models import load_model
from nltk.corpus import stopwords
from rake_nltk import Rake




def main():
    # Load the model
    model = load_model('model/sentiment_analysis_model.h5')

    new_data = pd.read_csv("./exchange/input/input.csv", sep=";")

    # Train the tokenizer
    tokenizer = Tokenizer(num_words=5000, split=" ")
    tokenizer.fit_on_texts(new_data['review_thoughts'].values)

    # Tokenizer
    #tokenizer = Tokenizer(num_words=5000, split=" ")

    # Define the predict function
    def predict(text, include_neutral=True):
        # Set maxlen to the value used in training
        maxlen = 100  # Or whatever value you used in training

        start_at = time.time()

        # Tokenize text
        x_test = pad_sequences(tokenizer.texts_to_sequences([text]), maxlen=maxlen)

        # Predict
        score = model.predict([x_test])[0]

        # Decode sentiment
        if include_neutral:
            label_idx = np.argmax(score)
            label = ["NEGATIVE", "NEUTRAL", "POSITIVE"][label_idx]
        else:
            label = "NEGATIVE" if score[0] > 0.5 else "POSITIVE"

        return {"label": label, "score": float(score[label_idx]),
                "elapsed_time": time.time() - start_at}

    # Predict sentiment for new data
    new_data['predicted_sentiment'] = new_data['review_thoughts'].apply(lambda x: predict(x))

    # Categorize reviews based on sentiment score
    new_data['sentiment_category'] = new_data['predicted_sentiment'].apply(lambda x: x['label'])

    print(new_data)

    # Save the dataframe with new sentiment information
    new_data.to_csv("./exchange/output/output_with_sentiments.csv", sep=';', index=False, encoding='utf-8',
                    quoting=csv.QUOTE_ALL)

    # Count the sentiment categories
    sentiment_counts = new_data['sentiment_category'].value_counts()

    print(sentiment_counts)

    nltk.download('punkt')
    # NLTK Stop word list
    stopwordss = set(stopwords.words('english'))

    def extract_keywords(text):
        r = Rake(stopwords=stopwordss)  # Uses stopwords for english from NLTK, and all puntuation characters.
        r.extract_keywords_from_text(text)
        return r.get_ranked_phrases()  # To get keyword phrases ranked highest to lowest.

    new_data['keywords'] = new_data['review_thoughts'].apply(extract_keywords)

    # Save the dataframe with new sentiment information
    new_data.to_csv("./exchange/output/output_with_sentiments_keywords.csv", sep=';', index=False, encoding='utf-8',
                    quoting=csv.QUOTE_ALL)

    print("[LOG] Data processing done.")


if __name__ == "__main__":
    main()