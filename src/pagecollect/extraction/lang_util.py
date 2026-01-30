import langdetect

def get_text_lang(text):
    """
    Detect the language of a text snippet.
    Only the first 100 characters are used to reduce cost
    """
    try:
        ln = langdetect.detect(text[:100])
        return ln
    except Exception:
        return None
