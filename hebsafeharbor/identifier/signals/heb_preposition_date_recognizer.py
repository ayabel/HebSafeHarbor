from typing import Optional, List
from presidio_analyzer.predefined_recognizers import DateRecognizer
from presidio_analyzer import Pattern

class PrepositionDateRecognizer(DateRecognizer):
    """
    A class which extends the DateRecognizer (@Presidio) and recognizes dates that contain a Hebrew preposition (ב9.9.1999)
    """   
    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "he",
        supported_entity: str = "DATE",
    ):
        # take the default patterns from the DateRecognizer class and augment them with a preposition
        patterns = self.PATTERNS
        AUG_PATTERNS = []
        for p in patterns:
            pattern_dict = p.to_dict()
            pattern = pattern_dict['regex']
            new_regex = pattern[:pattern.index(r'\b')+2] + '(?:ה|ב|מ|מה?)' + pattern[pattern.index(r'\b')+2:]
            pattern_dict['regex'] = new_regex
            AUG_PATTERNS.append(Pattern.from_dict(pattern_dict))
        
        super().__init__(
            supported_entity=supported_entity,
            patterns=AUG_PATTERNS,
            context=context,
            supported_language=supported_language,
        )

