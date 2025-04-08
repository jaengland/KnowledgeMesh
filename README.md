# Knowledge Mesh


## Local Use
- ./KnowledgeMesh/local/demo_backend: `docker build -t multi-service-stack .`
- ./KnowledgeMesh/local/demo_backend: `docker run -it -p 5432:5432 -p 9200:9200 multi-service-stack`
- ./KnowledgeMesh: `docker build -t knowledge-mesh .`
- ./KnowledgeMesh: `docker run -it -p 80:5000 knowledge-mesh`

## TODO:
- The results are ugly
- add a report button
- add a report page
  - make a standard dropdown for types of reports for automated handling?
- kerberos auth

