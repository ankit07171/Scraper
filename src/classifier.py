# from textblob import TextBlob

# spam_words = [
#     "follow", "subscribe", "free", "click",
#     "visit", "giveaway", "earn", "promo", "dm"
# ]

# generic_words = [
#     "nice", "ok", "okay", "good",
#     "cool", "wow", "great"
# ]

# def is_spam(text):
#     return any(word in text for word in spam_words)

# def is_generic(text):
#     return text in generic_words or len(text.split()) <= 2

# def sentiment_label(text):
#     polarity = TextBlob(text).sentiment.polarity
#     if polarity > 0.1:
#         return "Positive"
#     elif polarity < -0.1:
#         return "Negative"
#     else:
#         return "Neutral"

# def classify_comment(text):
#     if is_spam(text):
#         return "Spam"
#     elif is_generic(text):
#         return "Generic"
#     else:
#         return sentiment_label(text)
from textblob import TextBlob

spam_words = [
    "follow", "subscribe", "free", "click",
    "visit", "giveaway", "earn", "promo", "dm"
]

generic_words = [
    "nice", "ok", "okay", "good",
    "cool", "wow", "great"
]

def is_spam(text):
    return any(word in text for word in spam_words)

def is_generic(text):
    return text in generic_words or len(text.split()) <= 2

def sentiment_label(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"

def classify_comment(text):
    if is_spam(text):
        return "Spam"
    elif is_generic(text):
        return "Generic"
    else:
        return sentiment_label(text)
