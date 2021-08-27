import click
from rdflib import Graph
from sqlite_utils import Database
from .mappings import rdf_to_sqlite

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
