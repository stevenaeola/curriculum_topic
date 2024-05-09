from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer


import json
import pandas as pd

with open("scraping/topic_text.json", "r") as file:
    topic_texts = json.load(file)

with open("iticse2023_wg6_electives_non_uk.json", "r") as file:
    iticse_texts = json.load(file)

vectorizer_model = CountVectorizer(stop_words="english", ngram_range = (1, 2))

topic_model = BERTopic(vectorizer_model=vectorizer_model, min_topic_size=5)
topics, probs = topic_model.fit_transform(topic_texts + iticse_texts)
topic_model.get_topic_info().to_json("topic_model_info.json")

with open("scraping/topic_assignment.json", "w") as file:
    json.dump(topics[:len(topic_texts)], file)

with open("iticse_topic_assignment.json", "w") as file:
    json.dump(topics[len(topic_texts):], file)
