from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction import text 



import json
import pandas as pd

my_additional_stop_words = [
    'andor',
    'bschons',
    'cdt',
    'course',
    'description',
    'horizon',
    'mcomphons',
    'module',
    'nbsp',
    'nbspnbsp',
    'phd', 
    'purpose',
    'skill',
    'skills',
    'student',
    'students',
    'using'
    ]

with open("scraping/topic_text.json", "r") as file:
    topic_texts = json.load(file)

with open("iticse2023_wg6_electives_non_uk.json", "r") as file:
    iticse_texts = json.load(file)

stop_words = text.ENGLISH_STOP_WORDS.union(my_additional_stop_words)

vectorizer_model = CountVectorizer(stop_words="english", ngram_range = (1, 2))

topic_model = BERTopic(vectorizer_model=vectorizer_model, min_topic_size=5)
topics, probs = topic_model.fit_transform(topic_texts + iticse_texts)
topic_model.get_topic_info().to_json("topic_model_info.json")
topic_model.visualize_topics()

with open("scraping/topic_assignment.json", "w") as file:
    json.dump(topics[:len(topic_texts)], file)

with open("iticse_topic_assignment.json", "w") as file:
    json.dump(topics[len(topic_texts):], file)

hierarchical_topics = topic_model.hierarchical_topics(docs)
topic_model.visualize_hierarchy(hierarchical_topics=hierarchical_topics)