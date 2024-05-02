from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer


import json
import pandas as pd

with open("scraping/topic_text.json", "r") as file:
    topic_texts = json.load(file)


vectorizer_model = CountVectorizer(stop_words="english")

topic_model = BERTopic(vectorizer_model=vectorizer_model)
topics, probs = topic_model.fit_transform(topic_texts)
topic_model.get_topic_info().to_json("topic_model_info.json")

with open("scraping/topic_assignment.json", "w") as file:
    json.dump(topics, file)
