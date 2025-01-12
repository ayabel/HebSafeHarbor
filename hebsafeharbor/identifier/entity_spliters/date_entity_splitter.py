from hebsafeharbor import Doc
from hebsafeharbor.common.terms_recognizer import TermsRecognizer
from hebsafeharbor.identifier.entity_spliters.entity_splitter import EntitySplitter


class DateEntitySplitter(EntitySplitter):
    """
    This entity splitter decides for each DATE / DATE_TIME entity whether it describes a birth data or a medical date
    and updates the entity type accordingly.
    """

    BIRTH_DATE_CONTEXT = ["נולד", "נולדה", "תאריך לידה", "ת.לידה"]
    WINDOW_SIZE = 10

    def __init__(self):
        """
        Initializes DateEntitySplitter
        """
        super().__init__(supported_entity_types=["DATE", "DATE_TIME"])
        self.birth_date_terms_recognizer = TermsRecognizer(DateEntitySplitter.BIRTH_DATE_CONTEXT)

    def __call__(self, doc: Doc) -> Doc:
        """
        This method changes the type of any date entity into more specific value - BIRTH_DATE or MEDICAL_DATE.

        :param doc: document which stores the recognized entities before and after executing the DateEntitySplitter
        """
        date_entities = self.filter_relevant_entities(doc)
        if len(date_entities) == 0:
            return doc

        birth_date_offsets = self.birth_date_terms_recognizer(doc.text)
        if len(birth_date_offsets) == 0:
            for entity in date_entities:
                entity.entity_type = "MEDICAL_DATE"
        birth_date_end_offsets = list(map(lambda offset: offset[0] + offset[1] - 1, birth_date_offsets))

        for entity in date_entities:
            if any(entity.start - end_offset < DateEntitySplitter.WINDOW_SIZE for end_offset in birth_date_end_offsets):
                entity.entity_type = "BIRTH_DATE"
            else:
                entity.entity_type = "MEDICAL_DATE"

        return doc