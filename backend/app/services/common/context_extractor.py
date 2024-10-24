import spacy
from summa import keywords


class ContextExtractor:
    def __init__(self):
        # Load a spaCy model
        self.nlp = spacy.load("en_core_web_sm")

    def extract_entities(self, text):
        doc = self.nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]

    def tag_parts_of_speech(self, text):
        doc = self.nlp(text)
        return [(token.text, token.pos_) for token in doc]

    def parse_dependency(self, text):
        doc = self.nlp(text)
        return [(token.text, token.dep_, token.head.text) for token in doc]

    def extract_keywords(self, text):
        return keywords.keywords(text)


if __name__ == "__main__":
    text = "Apple is looking at buying U.K. startup for $1 billion"
    context_extractor = ContextExtractor()
    entities = context_extractor.extract_entities(text)
    pos_tags = context_extractor.tag_parts_of_speech(text)
    dependency_parse = context_extractor.parse_dependency(text)
    extracted_keywords = context_extractor.extract_keywords(text)
    print(f"Entities: {entities}")
    print(f"POS Tags: {pos_tags}")
    print(f"Dependency Parse: {dependency_parse}")
    print(f"Keywords: {extracted_keywords}")
