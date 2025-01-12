"""
A script to extract wiki datalists in Hebrew given a catagory wiki_id
- Medication wiki_id is Q12140
- Body_parts can be obtained by union over "anatomical structure" Q4936952, "anatomical region" (Q17781690)\
and tagma (Q1402830)
- hospital (Q16917)
- city (Q515)
- government program (Q22222786)

You can explore wikidata for ideas of relevant categories https://www.wikidata.org/wiki/Wikidata:Main_Page

Usage example:
python wikidata_lexicon_extractor.py Q515 cities_lexicon.py CITIES_LEXICON
"""

from typing import List
import requests
import re
import json
import argparse

WIKI_DATA_URL = 'https://query.wikidata.org/sparql'
QUERY_TEMPLATE = """
SELECT ?item ?itemLabel ?itemAltLabel
WHERE 
{
  ?item wdt:P31 wd:<WIKI_ID>.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "he". } # Helps get the label in your language, if not, then en language
}
"""

EN_LETTERS_RE = re.compile(r"[a-zA-Z]") # used to filter out terms with En letters
HE_LETTERS_RE = re.compile(r"[ \-א-ת0-9]") # used to clean "nikud"


def wikidata_query(wiki_id: str):
    r = requests.get(WIKI_DATA_URL, params={'format': 'json', 'query': QUERY_TEMPLATE.replace("<WIKI_ID>", wiki_id)})
    data = r.json()
    return data["results"]['bindings']


def process_wikidata_response(data: List) -> List[str]:
    all_names = set()
    for item in data:
        label = item['item']['value']
        alt_labels = item['itemAltLabel']['value'].split(', ') if 'itemAltLabel' in item else []
        for name in [label] + alt_labels:
            if not EN_LETTERS_RE.findall(name):
                name_cleaned = ''.join(HE_LETTERS_RE.findall(name))
                if name_cleaned:
                    all_names.add(name_cleaned)
    return list(all_names)


def save_python_file(all_names: List[str], output_file: str, lexicon_name: str):
    with open(output_file, 'w', encoding="utf-8") as fp:
        fp.write(f"{lexicon_name} = [\n")
        for name in all_names:
            fp.write(f'\t"{name}",\n')
        fp.write(']\n')


def main(wiki_id: str, output_file: str, lexicon_name: str):
    data = wikidata_query(wiki_id)
    all_names = process_wikidata_response(data)
    save_python_file(all_names, output_file, lexicon_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('wiki_id', help="a wikiID you want to list all instances of")
    parser.add_argument('output_file', help="output python file")
    parser.add_argument('lexicon_name', help="variable name in python file")

    args = parser.parse_args()

    main(args.wiki_id, args.output_file, args.lexicon_name)
