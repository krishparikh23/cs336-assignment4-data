import fasttext

_model = fasttext.load_model("data/classifiers/lid.176.bin")


def identify_language(text: str) -> tuple[str, float]:
    """
    Identify the main language of the given text using fastText.
    Returns a tuple (language_code, confidence_score).
    """
    cleaned_text = text.replace("\n", "") # predict processes one line at a time

    labels, probabilities = _model.predict(cleaned_text, k=1)
    label = labels[0]
    score = probabilities[0]

    if label.startswith("__label__"):
        lang = label[len("__label__"):]
    else:
        lang = label

    return lang, score