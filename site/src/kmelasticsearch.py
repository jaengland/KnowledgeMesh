from elasticsearch import Elasticsearch


def search_records(search_string: str, elastic_search_url: str):
    es = Elasticsearch(elastic_search_url)
    query = {
        "query": {
            "query_string": {
                "query": search_string,  # Replace with your search keyword
                "fields": ["title", "description", "tags"]
            }
        },
        "collapse": {
            "field": "id"  # Collapses results so that each unique id appears only once
        }
    }

    # Execute the search query on the specified index
    response = es.search(index="records_index", body=query)
    results = []
    for hit in response['hits']['hits']:
        results.append(hit['_source'])
    return results


def get_latest(elastic_search_url: str):
    es = Elasticsearch(elastic_search_url)

    query = {
        "query": {
            "match_all": {}  # You can replace this with your specific query
        },
        "collapse": {
            "field": "id",
            "inner_hits": {
                "name": "most_recent_doc",
                "size": 1,
                "sort": [
                    {"updated": "desc"}  # Assuming "timestamp" is the field with the date info
                ]
            }
        },
        "sort": [
            {"updated": "desc"}
        ],
        "size": 10
    }

    response = es.search(index="records_index", body=query)

    results = []
    for hit in response['hits']['hits']:
        results.append(hit['_source'])
    return results


def get_user_records(user_id, elastic_search_url: str):
    es = Elasticsearch(elastic_search_url)

    query = {
        "query": {
            "query_string": {
                "query": user_id,  # Replace with your search keyword
                "fields": ["samaccountname"]
            }
        },
        "collapse": {
            "field": "id"  # Collapses results so that each unique id appears only once
        }
    }

    response = es.search(index="records_index", body=query)
    results = []
    for hit in response['hits']['hits']:
        results.append(hit['_source'])
    return results

def delete_record(record, elastic_search_url: str):
    es = Elasticsearch(elastic_search_url)

    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"id": record['id']}},
                    {"match": {"samaccountname": record['samaccountname']}}
                ]
            }
        }
    }

    # Execute the search query on the specified index
    try:
        response = es.delete_by_query(index='records_index', body=query)
        return True
    except Exception as e:
        print(f'error deleting records {record}: {e}')
        return False


