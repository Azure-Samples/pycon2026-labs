from .init import client, vector_store
from langchain_core.documents import Document
from typing import List, Optional, Union

from model.travel import Ship,Itinerary


def results_to_ship(result:Document) -> Ship:
    return Ship(name = result.metadata["name"],
                        description = result.metadata["description"],
                        amenities= result.metadata["amenities"])


def get_ship_by_name(name:str)->str:
    db = client["travel"]
    collection_name = db["ships"]
    normalized_name = name.strip()
    print(f"-{normalized_name}-")

    ship = collection_name.find_one(
        {"metadata.name": {"$regex": f"^{normalized_name}$", "$options": "i"}}
    )

    if ship is None:
        ship = collection_name.find_one({"name": {"$regex": f"^{normalized_name}$", "$options": "i"}})

    if ship is None:
        print("ship not found")
        return ''

    if 'metadata' in ship and 'shipid' in ship['metadata']:
        return ship['metadata']['shipid']

    if 'shipid' in ship:
        return ship['shipid']

    print('ship id not found')
    return ''


def format_currency(amount: float) -> str:
    return f"${amount:,.2f}"


def destination_search(query: str) -> list[dict]:
    db = client["travel"]
    collection_name = db["destinations"]
    normalized_query = query.strip().lower()

    destinations = list(
        collection_name.find({}, {"_id": 0, "name": 1, "location": 1, "description": 1, "activities": 1})
    )

    direct_matches = [
        destination for destination in destinations if destination.get("name", "").lower() in normalized_query
    ]

    if direct_matches:
        return direct_matches

    query_terms = {
        term for term in normalized_query.replace("?", " ").replace(",", " ").split() if len(term) > 3
    }

    scored_matches: list[tuple[int, dict]] = []
    for destination in destinations:
        haystack = " ".join(
            [
                destination.get("name", ""),
                destination.get("location", ""),
                destination.get("description", ""),
                " ".join(destination.get("activities", [])),
            ]
        ).lower()
        score = sum(1 for term in query_terms if term in haystack)
        if score > 0:
            scored_matches.append((score, destination))

    scored_matches.sort(key=lambda item: item[0], reverse=True)
    return [destination for _, destination in scored_matches[:2]]


def itnerary_search(name:str) -> list[Itinerary]:
    data = []
    db = client["travel"]
    collection_name = db["itinerary"]
    id = get_ship_by_name(name)
    if id != '':
        print(id)
        cursor  = collection_name.find({'ship.shipid':id})
        for item in cursor:
            data.append(Itinerary(ShipID=item['ship']['shipid'],
                                Name=item['name'], Rooms=[f" room {p['name']} price {format_currency(p['price'])} " for p in item['prices']],
                                Schedule=[f" day {p['Day']} {p['type']} location {p['location']} " for p in item['itinerary']]
                        ))
        print(data)
    return data



def similarity_search(query:str)-> list[Ship]:

    docs = vector_store.similarity_search_with_score(query,2)

    # Cosine Similarity:
    #It measures the cosine of the angle between two vectors in an n-dimensional space.
    #The values of similarity metrics typically range between 0 and 1, with higher values indicating greater similarity between the vectors.
    docs_filters = [doc for doc, score  in docs if score >=.78]

    # List the scores for documents
    for doc, score  in docs:
        print(score)

    # Print number of documents passing score threshold
    print(len(docs_filters))
  
    return [results_to_ship(document) for document in docs_filters]
  

