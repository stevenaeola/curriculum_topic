from bertopic import BERTopic
import json
import pandas as pd

with open("scraping/topic_text.json", "r") as file:
    topic_texts = json.load(file)

topic_model = BERTopic()
topics, probs = topic_model.fit_transform(topic_texts)
topic_model.get_topic_info().to_json("topic_model_info.json")
