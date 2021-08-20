# rdf_to_sqlite
[![PyPI](https://img.shields.io/pypi/v/rdf-to-sqlite.svg)](https://pypi.org/project/rdf-to-sqlite/)
[![Changelog](https://img.shields.io/github/v/release/bradleypallen/rdf-to-sqlite?include_prereleases&label=changelog)](https://github.com/bradleypallen/rdf-to-sqlite/releases)
[![Tests](https://github.com/bradleypallen/rdf-to-sqlite/workflows/Test/badge.svg)](https://github.com/bradleypallen/rdf-to-sqlite/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/bradleypallen/rdf-to-sqlite/blob/main/LICENSE)

Load the contents of an RDF file into a set of SQLite database tables.

```
$ rdf-to-sqlite --help
Usage: rdf-to-sqlite [OPTIONS] DB_PATH RDF_FILE

  Convert an RDF file to SQLite

Options:
  --version                       Show the version and exit.
  --context TEXT                  URL or file containing a JSON-LD context
  --format [html|n3|nquads|nt|rdfa|rdfa1.0|rdfa1.1|trix|turtle|xml|json-ld]
                                  RDF serialization format  [required]
  --help                          Show this message and exit.
```
## Usage
Given an RDF file `example.ttl` containing the following:
```
@prefix ns1: <http://schema.org/> .

<http://www.janedoe.com/> a ns1:Person ;
    ns1:jobTitle "Professor" ;
    ns1:name "Jane Doe" ;
    ns1:telephone "(425) 123-4567" .
```

Running this command:
```
$ rdf-to-sqlite example.db example.ttl --format turtle --context https://schema.org/docs/jsonldcontext.jsonld
```

Will create a database file `example.db` with this schema, using a property
table approach to RDF storage on relational databases [1], [2]:
```
CREATE TABLE [Person] (
   [@context] TEXT,
   [id] TEXT PRIMARY KEY,
   [jobTitle] TEXT,
   [name] TEXT,
   [telephone] TEXT
);
CREATE TABLE [Person_rdf:type] (
   [subject] TEXT,
   [predicate] TEXT,
   [object] TEXT,
   PRIMARY KEY ([subject], [object])
);
```

## License
MIT. See the LICENSE file for the copyright notice.

## References
[[1]](https://doi.org/10.1145/1815948.1815953)  Sakr, S. and Al-Naymat, G., 2010.
Relational processing of RDF queries: a survey. ACM SIGMOD Record, 38(4), pp.23-28.

[[2]](https://arxiv.org/abs/2009.10331) Ali, W., Saleem, M., Yao, B., Hogan, A.
and Ngomo, A.C.N., 2020. Storage, indexing, query processing, and benchmarking
in centralized and distributed rdf engines: A survey. arXiv preprint arXiv:2009.10331.
