import spacy
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
from typing import List, Union
from src.models import Item, Language


class Matcher:
    """
    A matcher that finds the best items for answering a particular equipment query.
    """

    def __init__(self, language: Language):
        self.nlp = spacy.load(
            "en_core_web_sm" if language == Language.EN else "fr_core_news_sm",
            exclude=["ner"],
        )
        self.model = SentenceTransformer("distiluse-base-multilingual-cased-v1")

    def find_matches(self, query: Item, candidates: List[Item]) -> List[Item]:
        """
        Finds the best matches for the given query, returning the objects sorted in order of
        similarity (descending order).
        """
        print("Finding matches...")
        query_emb = self._compute_embedding(self._lemmatize(query.to_sentence()))
        candidates_embs = self._compute_embedding(
            list(map(lambda c: self._lemmatize(c.to_sentence()), candidates))
        )
        similarities = []
        for i, p in enumerate(candidates_embs):
            sim = self._cosine_similarity(query_emb, p)
            similarities.append((i, sim))
        indexes, _ = zip(
            *list(
                filter(
                    lambda s: s[1] >= 0.6,
                    sorted(similarities, key=lambda p: p[1], reverse=True),
                )
            )
        )
        return [candidates[i] for i in indexes]

    def _lemmatize(self, sentence: str):
        return " ".join([w.lemma_ for w in self.nlp(sentence) if not w.is_stop])

    def _compute_embedding(self, sentences: Union[str, List[str]]):
        return self.model.encode(sentences)

    def _cosine_similarity(self, v1, v2):
        return 1 - cosine(v1, v2)
