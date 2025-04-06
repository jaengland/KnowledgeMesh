# Knowledge Mesh


## Local Use
- ./KnowledgeMesh/local/demo_backend: `docker build -t multi-service-stack .`
- ./KnowledgeMesh/local/demo_backend: `docker run -it -p 5432:5432 -p 9200:9200 multi-service-stack`
- ./KnowledgeMesh: `docker build -t knowledge-mesh .`
- ./KnowledgeMesh: `docker run -it -p 80:5000 knowledge-mesh`

## TODO:
- move the list rendering from python to javascript
- make the search button do something
- add an insert record page
- The results are ugly
- add a report button
- add a report page
  - make a standard dropdown for types of reports for automated handling?
- add a my profile button
- on my profile page let users delete their own entries?
- kerberos auth

