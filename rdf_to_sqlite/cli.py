import click, json
from rdflib import Graph, URIRef, BNode
from rdflib.namespace import RDF
from rdflib.plugins.shared.jsonld.context import Context
from sqlite_utils import Database

def rdf_to_sqlite(graph, context, db):
    ctxt = Context(source=context)
    tables = set([ o for o in graph.objects(predicate=RDF.type)])
    properties = set([ p for p in graph.predicates() ])
    # We assume that any property with only IRIs or blank nodes as objects is a
    # reference property. RDF that mixes literals with IRIs or blank nodes in
    # the range of a given property will end up with that property treated
    # as a literal property, which will result in funky literal property values.
    reference_properties = set([ p for p in properties if all([ isinstance(o, URIRef) or isinstance(o, BNode) for o in graph.objects(predicate=p)])])
    literal_properties = properties - reference_properties
    instance_triples = {}
    reference_triples = {}
    for table in tables:
        instance_triples[table] = Graph()
        reference_triples[table] = {}
        instances = graph.subjects(predicate=RDF.type, object=table)
        for instance in instances:
            for s, p, o in graph.triples((instance, None, None)):
                if p in literal_properties:
                    instance_triples[table].add((s, p, o))
                else:
                    if f'{p}' not in reference_triples[table]:
                        reference_triples[table][f'{p}'] = Graph()
                    reference_triples[table][f'{p}'].add((s, p, o))
    for table in tables:
        table_name = ctxt.to_symbol(table)
        instance_triples_jsonld = json.loads(instance_triples[table].serialize(format='json-ld', context=context))
        # Bug: need to address literal datatypes f.g. {"@type": "xsd:date", "@value": "2020-06-22"}
        if "@graph" in instance_triples_jsonld:
            rows = instance_triples_jsonld["@graph"]
        else:
            # Bug: need to remove @context from singleton JSON objects, otherwise
            # it is treated as a column/value
            rows = [ instance_triples_jsonld ]
        db[table_name].insert_all(rows, pk='id', alter=True)
    for table in tables:
        for r in reference_triples[table]:
            table_name = f'{ctxt.to_symbol(table)}_{ctxt.to_symbol(r)}'
            rows = []
            for s, p, o in reference_triples[table][r].triples((None, None, None)) :
                if isinstance(s, BNode):
                    subj = s.n3()
                else:
                    subj = ctxt.to_symbol(s)
                prop = ctxt.to_symbol(p)
                if isinstance(o, BNode):
                    obj = o.n3()
                else:
                    obj = ctxt.to_symbol(o)
                # Issue: we could save some space by removing the predicate column,
                # but this will complicate recovery of predicate CURIEs/IRIs
                # during inverse mapping (if and when we add that capability.)
                row = { 'subject': subj, 'predicate': prop, 'object': obj }
                rows.append(row)
            db[table_name].insert_all(rows, pk=('subject', 'object'))

@click.command()
@click.version_option()
@click.argument("db_path", type=click.Path(file_okay=True, dir_okay=False, allow_dash=False))
@click.argument("rdf_file", type=click.Path(file_okay=True, dir_okay=False, allow_dash=False))
@click.option("--context", type=click.STRING, help="URL or file containing a JSON-LD context")
@click.option("--format", required=True, type=click.Choice([
    'html', 'n3', 'nquads', 'nt', 'rdfa',
    'rdfa1.0', 'rdfa1.1', 'trix',
    'turtle', 'xml', 'json-ld'], case_sensitive=False), help='RDF serialization format')
def cli(db_path, rdf_file, context, format):
    "Convert an RDF file to SQLite"
    db = Database(db_path)
    graph = Graph().parse(rdf_file, format=format)
    rdf_to_sqlite(graph, context, db)
    click.echo(f'Generated {db_path} ({sum([ table.count for table in db.tables ])} rows in {len(db.tables)} tables)')

if __name__ == '__main__':
    cli()
