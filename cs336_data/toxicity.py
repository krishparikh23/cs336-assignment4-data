import fasttext

_nsfw_model = fasttext.load_model("data/classifiers/dolma_fasttext_nsfw_jigsaw_model.bin")
_toxic_model = fasttext.load_model("data/classifiers/dolma_fasttext_hatespeech_jigsaw_model.bin")


def classify_nsfw(text: str):
    """
    Classify input text as 'nsfw' or 'non-nsfw' with a confidence score.
    """
    labels, scores = _nsfw_model.predict(text, k=1)
    label = labels[0].replace("__label__", "")
    confidence = float(scores[0])
    return label, confidence

def classify_toxic_speech(text: str):
    """
    Classify input text as 'toxic' or 'non-toxic' with a confidence score.
    """
    labels, scores = _toxic_model.predict(text, k=1)
    label = labels[0].replace("__label__", "")
    confidence = float(scores[0])
    return label, confidence 