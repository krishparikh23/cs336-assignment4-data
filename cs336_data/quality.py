def gopher_quality_filter(text: str) -> bool:
    """
    Implements a subset of the Gopher quality filters.
    """
    # Reject documents with word count <50 or >100000
    tokens = text.split()
    word_count = len(tokens)
    if word_count < 50 or word_count > 100_000:
        return False
    # Reject documents with mean word length <3 or >10
    total_length = sum(len(token) for token in tokens)
    mean_length = total_length / word_count
    if mean_length < 3 or mean_length > 10:
        return False
    # Reject if >30% of lines end with an ellipsis '...'
    lines = text.splitlines()
    if lines:
        ellipsis_count = sum(1 for line in lines if line.rstrip().endswith('...'))
        if ellipsis_count / len(lines) > 0.3:
            return False
    # Reject if <80% of words have at least one alphabetic character
    alpha_count = sum(1 for token in tokens if any(c.isalpha() for c in token))
    if alpha_count / word_count < 0.8:
        return False
    return True 