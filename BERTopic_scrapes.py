from bertopic import BERTopic
import json

with open("scraping/topic_text.json", "r") as file:
    topic_texts = json.load(file)

topic_model = BERTopic()
topics, probs = topic_model.fit_transform(topic_texts)
print(topic_model.get_topic_info())
