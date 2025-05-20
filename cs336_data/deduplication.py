import os
from pathlib import Path
from collections import Counter
from typing import Sequence
import unicodedata
import string
import mmh3
from collections import defaultdict


def exact_line_deduplication(
    input_files: Sequence[os.PathLike], output_directory: os.PathLike
) -> None:
    """
    Perform exact line deduplication over a list of files.
    Writes each input file to the output directory, removing lines that occur more than once across all input files.
    """
    line_counts: Counter[str] = Counter()
    for file_path in input_files:
        path = Path(file_path)
        with open(path, 'r') as f:
            for line in f:
                line_counts[line] += 1

    for file_path in input_files:
        path = Path(file_path)
        output_path = Path(output_directory) / path.name
        with open(path, 'r') as f_in, open(output_path, 'w') as f_out:
            for line in f_in:
                if line_counts[line] == 1:
                    f_out.write(line)

def minhash_deduplication(
    input_files: Sequence[os.PathLike],
    num_hashes: int,
    num_bands: int,
    ngrams: int,
    jaccard_threshold: float,
    output_directory: os.PathLike,
) -> None:
    """
    Perform fuzzy document deduplication via minhash + LSH.
    Writes one representative per duplicate cluster to output_directory.
    """
    # Read and normalize documents
    paths = [Path(p) for p in input_files]
    texts = [p.read_text() for p in paths]

    def normalize(text: str) -> str:
        # Unicode normalize, remove accents
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if not unicodedata.combining(c))
        # Lowercase
        text = text.lower()
        # Remove punctuation
        text = ''.join(c if c not in string.punctuation else ' ' for c in text)
        # Normalize whitespace
        return ' '.join(text.split())

    normalized_texts = [normalize(t) for t in texts]
    # Build ngram sets
    docs_ngrams = []
    for nt in normalized_texts:
        tokens = nt.split()
        if len(tokens) < ngrams:
            ngram_set = set()
        else:
            ngram_set = {
                ' '.join(tokens[i:i+ngrams])
                for i in range(len(tokens) - ngrams + 1)
            }
        docs_ngrams.append(ngram_set)

    # Compute minhash signatures
    signatures = []
    for s in docs_ngrams:
        sig = []
        for seed in range(num_hashes):
            min_hash = None
            for ngram in s:
                h = mmh3.hash(ngram, seed, signed=False)
                if min_hash is None or h < min_hash:
                    min_hash = h
            sig.append(min_hash if min_hash is not None else 0)
        signatures.append(sig)

    # LSH bucketing
    rows = num_hashes // num_bands
    buckets = defaultdict(list)
    for idx, sig in enumerate(signatures):
        for band in range(num_bands):
            start = band * rows
            end = start + rows
            band_sig = tuple(sig[start:end])
            buckets[(band, band_sig)].append(idx)

    # Union-find for clusters
    parent = list(range(len(paths)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[ry] = rx

    # Candidate pairs -> refine by Jaccard
    for idxs in buckets.values():
        if len(idxs) > 1:
            for i in range(len(idxs)):
                for j in range(i+1, len(idxs)):
                    a, b = idxs[i], idxs[j]
                    set_a, set_b = docs_ngrams[a], docs_ngrams[b]
                    if not set_a and not set_b:
                        jaccard = 1.0
                    else:
                        inter = len(set_a & set_b)
                        union_sz = len(set_a | set_b)
                        jaccard = inter / union_sz if union_sz > 0 else 0.0
                    if jaccard >= jaccard_threshold:
                        union(a, b)

    # Collect clusters
    clusters = defaultdict(list)
    for i in range(len(paths)):
        clusters[find(i)].append(i)

    # Determine which indices to keep
    keep = set()
    for cluster in clusters.values():
        # Always keep one per cluster
        keep.add(min(cluster))

    # Write out kept documents
    os.makedirs(output_directory, exist_ok=True)
    for idx in keep:
        out_path = Path(output_directory) / paths[idx].name
        with open(out_path, 'w') as f:
            f.write(texts[idx]) 