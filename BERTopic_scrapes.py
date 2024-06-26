from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction import text 



import json
import pandas as pd

my_additional_stop_words_v1 = [
    'andor',
    'assessment',
    'bschons',
    'cdt',
    'course',
    'defined',
    'description',
    'horizon',
    'including',
    'mcomphons',
    'module',
    'nbsp',
    'nbspnbsp',
    'nbspnbspnbsp',
    'nbspcan',
    'phd', 
    'problems',
    'purpose',
    'skill',
    'skills',
    'staff',
    'student',
    'students',
    'using'
    ]

my_additional_stop_words_v2 = [
  "understanding",
  "principles",
  "specific",
  "degree",
  "allow",
]
with open("scraping/topic_text.json", "r") as file:
    topic_texts = json.load(file)

with open("iticse2023_wg6_electives_non_uk.json", "r") as file:
    iticse_texts = json.load(file)

stop_words = list(text.ENGLISH_STOP_WORDS) + my_additional_stop_words_v1 + my_additional_stop_words_v2


vectorizer_model = CountVectorizer(stop_words=stop_words, ngram_range = (1, 2))

topic_model = BERTopic(vectorizer_model=vectorizer_model, min_topic_size=5)
topics, probs = topic_model.fit_transform(topic_texts + iticse_texts)
topic_model.get_topic_info().to_json("topic_model_info.json")
fig = topic_model.visualize_topics()
fig.write_html("topic_viz.html")

with open("scraping/topic_assignment.json", "w") as file:
    json.dump(topics[:len(topic_texts)], file, indent=1)

with open("iticse_topic_assignment.json", "w") as file:
    json.dump(topics[len(topic_texts):], file, indent=1)

topic_model.save("serialized", serialization="safetensors", save_ctfidf=True)

hierarchical_topics = topic_model.hierarchical_topics(topic_texts + iticse_texts)
fig = topic_model.visualize_hierarchy(hierarchical_topics=hierarchical_topics)
fig.write_html("hierarchy_viz.html")

