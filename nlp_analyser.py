import re
import numpy as np
import nltk
from nltk import pos_tag, RegexpParser
from nltk.tokenize import sent_tokenize, word_tokenize
nltk.download("punkt", quiet=True)
nltk.download("averaged_perceptron_tagger", quiet=True)

from vaderSentiment.vaderSentiment import (
    SentimentIntensityAnalyzer
)

from sklearn.feature_extraction.text import (
    TfidfVectorizer
)

# --------------------------------------------------
# TF-IDF KEY PHRASES
# --------------------------------------------------

def extract_key_phrases(text, top_n=10):

    try:

        sentences = sent_tokenize(text)

        if len(sentences) < 2:
            return []

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=200
        )

        matrix = vectorizer.fit_transform(sentences)

        scores = matrix.sum(axis=0).A1

        features = vectorizer.get_feature_names_out()

        ranked = sorted(
            zip(features, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            phrase
            for phrase, score in ranked[:top_n]
        ]

    except Exception:
        return []


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

def generate_summary(text, top_n=5):

    sentences = [

    s for s in sent_tokenize(text)

    if len(s.split()) > 8

    and "operator" not in s.lower()

    and "conference call" not in s.lower()

]

    if len(sentences) <= top_n:
        return " ".join(sentences)

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf = vectorizer.fit_transform(sentences)

    scores = tfidf.sum(axis=1)

    ranked = np.argsort(
        scores.A1
    )[::-1]

    selected = sorted(
        ranked[:top_n]
    )

    summary = " ".join(
        sentences[i]
        for i in selected
    )

    return summary

# --------------------------------------------------
# MANAGEMENT TONE
# --------------------------------------------------

def analyse_tone(text):

    analyzer = SentimentIntensityAnalyzer()

    score = analyzer.polarity_scores(text)

    compound = score["compound"]

    if compound > 0.2:
        overall = "Positive"

    elif compound < -0.2:
        overall = "Negative"

    else:
        overall = "Neutral"

    return {
        "overall": overall,
        "score": round(compound, 3)
    }

def detect_deviation(
    current_commitments,
    previous_commitments
):

    deviations = []

    prev_text = " ".join(
        x["commitment"]
        for x in previous_commitments
    )

    for item in current_commitments:

        current = item["commitment"]

        if current not in prev_text:

            deviations.append(current)

    return deviations[:5]
# --------------------------------------------------
# BUSINESS CHANGES
# --------------------------------------------------
def extract_business_changes(text, top_n=5):

    sentences = []

    for s in sent_tokenize(text):

        s = s.strip()

        # keep only meaningful sentences
        if len(s.split()) < 10:
            continue

        if len(s) > 400:
            continue

        sentences.append(s)

    if len(sentences) < 2:
        return []

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf = vectorizer.fit_transform(sentences)

    scores = np.asarray(
        tfidf.sum(axis=1)
    ).flatten()

    ranked_idx = scores.argsort()[::-1]

    changes = []

    for idx in ranked_idx:

        sentence = sentences[idx]

        # remove noisy sentences
        lower = sentence.lower()

        if any(
            x in lower
            for x in [
                "registered office",
                "company secretary",
                "conference call",
                "nse",
                "bse",
                "symbol",
                "scrip code",
                "exchange plaza",
                "mumbai"
            ]
        ):
            continue

        changes.append(sentence)

        if len(changes) >= top_n:
            break

    return changes
def extract_risks(text):

    analyzer = SentimentIntensityAnalyzer()

    risks = []

    for sentence in sent_tokenize(text):

        if len(sentence.split()) < 6:
            continue

        score = analyzer.polarity_scores(sentence)

        if score["compound"] < -0.25:

            risks.append({
                "risk":
                sentence.strip()
            })

    return risks[:10]



def extract_commitments(text):

    commitments = []

    for sentence in sent_tokenize(text):

        tokens = word_tokenize(sentence)

        tags = pos_tag(tokens)

        has_future = any(
            tag == "MD"
            for _, tag in tags
        )

        if has_future and len(sentence.split()) > 8:

            commitments.append({
                "commitment":
                sentence.strip()
            })

    return commitments[:10]
# --------------------------------------------------
# METRICS
# --------------------------------------------------

def extract_metrics(text):

    revenue_match = re.search(
        r"revenue.*?(\d+\.?\d*\s*%)",
        text,
        re.I | re.S
    )

    margin_match = re.search(
        r"margin.*?(\d+\.?\d*\s*%)",
        text,
        re.I | re.S
    )

    guidance_match = re.search(
        r"(guidance.*?[.])",
        text,
        re.I
    )

    return {

        "revenue_growth":
        revenue_match.group(1)
        if revenue_match else "",

        "margin":
        margin_match.group(1)
        if margin_match else "",

        "order_book":
        "",

        "guidance":
        guidance_match.group(1)
        if guidance_match else ""

    }

# --------------------------------------------------
# SINGLE QUARTER
# --------------------------------------------------
def analyse_quarter(transcript):

    text = transcript["text"]

    key_phrases = extract_key_phrases(text)

    earnings = [
        {"trigger": x}
        for x in key_phrases[:5]
    ]

    return {

        "quarter":
        transcript["quarter"],

        "summary":
        generate_summary(text),

        "management_tone":
        analyse_tone(text),

        "key_metrics_mentioned":
        extract_metrics(text),

        "earnings_triggers":
        earnings,

        "business_changes":
        extract_business_changes(text),

        "risks_and_issues":
        extract_risks(text),

        "commitments_made":
        extract_commitments(text),

        "deviations":
        []

    }

# --------------------------------------------------
# MAIN
# --------------------------------------------------
def run_full_analysis(
    transcripts,
    company_name=None,
    verbose=False
):

    quarterly_analyses = []

    # Analyze each quarter
    for transcript in transcripts:

        quarterly_analyses.append(
            analyse_quarter(transcript)
        )

    # Compare commitments with previous quarter
    for i in range(1, len(quarterly_analyses)):

        current = quarterly_analyses[i]

        previous = quarterly_analyses[i - 1]

        current["deviations"] = detect_deviation(
            current["commitments_made"],
            previous["commitments_made"]
        )

    # First quarter has no previous quarter
    if quarterly_analyses:
        quarterly_analyses[0]["deviations"] = []

    return {

        "company_name": company_name,

        "quarterly_analyses": quarterly_analyses

    }