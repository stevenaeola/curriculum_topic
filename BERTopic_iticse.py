from bertopic import BERTopic
import pandas as pd

all_electives = pd.read_csv("all_electives.csv")

# from https://medium.com/@jorlugaqui/how-to-strip-html-tags-from-a-string-in-python-7cb81a2bbf44
# adapted to replace with a space

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, ' ', text)

docs = map(remove_html_tag, all_electives['overview'])

topic_model = BERTopic()
topics, probs = topic_model.fit_transform(docs)
print(topic_model.get_topic_info())
