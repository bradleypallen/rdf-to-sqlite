import json, sqlite_utils
from rdf_to_sqlite.mappings import rdf_to_sqlite, sqlite_to_rdf
from sqlite_utils import Database
from rdflib import Graph
from pathlib import Path

TEST_RDF = """
{
    "@context": "https://schema.org/docs/jsonldcontext.jsonld",
    "@graph": [
        {
            "id": "https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2676",
            "text": "(The Travellers Companion Series, No. 76)",
            "type": "Comment"
        },
        {
            "author": { "id": "http://www.wikidata.org/entity/Q188176" },
            "comment": [
                { "id": "https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2676" },
                { "id": "https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2677" },
                { "id": "https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2678" },
                { "id": "https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2679" },
                { "id": "https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2680" },
                { "id": "https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2681"}
            ],
            "id": "https://wsburroughs.link/Book/abr40-a2a",
            "name": "Naked Lunch",
            "type": "Book"
        },
        {
            "id": "http://www.wikidata.org/entity/Q188176",
            "type": "Person"
        },
        {
            "id": "https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2677",
            "text": "Dustjacket designed by Burroughs.",
            "type": "Comment"
        },
        {
            "id": "https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2680",
            "text": "2nd printing [not to be confused with the “second issue” of the first printing (above)] issued without  dustjacket or decorative border around title page, and with price (“18 francs”) printed on back cover.",
            "type": "Comment"
        },
        {
            "id": "https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2679",
            "text": "1st printing comprised two “issues:”  1st issue: Price (“Francs: 1,500”) printed in lower right corner of back cover. 2nd issue: Price (“New Price NF 18”) stamped over old price in lower right corner of back cover, following the revaluation of the franc in January 1960.",
            "type": "Comment"
        },
        {
            "id": "https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2678",
            "text": "First copies printed issued without dustjacket. [M&M]",
            "type": "Comment"
        },
        {
            "id": "https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2681",
            "text": "3rd printing (1965) issued without dustjacket or decorative border around title page, and with price (“Francs: h18”) printed on back cover.",
            "type": "Comment"
        }
    ]
}
"""

EXPECTED_COMMENT_ROWS = [
 {'id': 'https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2678',
  'text': 'First copies printed issued without dustjacket. [M&M]'},
 {'id': 'https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2677',
  'text': 'Dustjacket designed by Burroughs.'},
 {'id': 'https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2681',
  'text': '3rd printing (1965) issued without dustjacket or decorative border around title page, and with price (“Francs: h18”) printed on back cover.'},
 {'id': 'https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2679',
  'text': '1st printing comprised two “issues:”  1st issue: Price (“Francs: 1,500”) printed in lower right corner of back cover. 2nd issue: Price (“New Price NF 18”) stamped over old price in lower right corner of back cover, following the revaluation of the franc in January 1960.'},
 {'id': 'https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2676',
  'text': '(The Travellers Companion Series, No. 76)'},
 {'id': 'https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2680',
  'text': '2nd printing [not to be confused with the “second issue” of the first printing (above)] issued without  dustjacket or decorative border around title page, and with price (“18 francs”) printed on back cover.'}
]

EXPECTED_BOOK_COMMENT_ROWS = [
 {'subject': 'https://wsburroughs.link/Book/abr40-a2a',
  'predicate': 'comment',
  'object': 'https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2680'},
 {'subject': 'https://wsburroughs.link/Book/abr40-a2a',
  'predicate': 'comment',
  'object': 'https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2678'},
 {'subject': 'https://wsburroughs.link/Book/abr40-a2a',
  'predicate': 'comment',
  'object': 'https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2676'},
 {'subject': 'https://wsburroughs.link/Book/abr40-a2a',
  'predicate': 'comment',
  'object': 'https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2681'},
 {'subject': 'https://wsburroughs.link/Book/abr40-a2a',
  'predicate': 'comment',
  'object': 'https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2677'},
 {'subject': 'https://wsburroughs.link/Book/abr40-a2a',
  'predicate': 'comment',
  'object': 'https://wsburroughs.link/Comment/n002ffd6182d84355b9967f0665f44e14b2679'}
]

def test_mapping_roundtrip(tmpdir):
    db_path = tmpdir / "test_mappings.db"
    rdf_path = tmpdir / "test_mappings.jsonld"
    Path(rdf_path).write_text(TEST_RDF)
    db = Database(str(db_path))
    graph_in = Graph().parse(str(rdf_path), format='json-ld')
    context = "https://schema.org/docs/jsonldcontext.jsonld"
    rdf_to_sqlite(graph_in, context, db)
    graph_out = sqlite_to_rdf(db, context)
    assert len(graph_in) == len(graph_out)
