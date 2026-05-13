from langchain_core.tools import tool
from langchain_core.documents import Document
from data.mongodb import travel
from model.travel import Ship


@tool
def vacation_lookup(input: str) -> str:
    """find information on vacations and trips"""

    print(f"[tool] vacation_lookup input={input}")

    destinations = travel.destination_search(input)
    if destinations:
        content = ""
        for destination in destinations:
            activities = "\n- ".join(destination.get("activities", []))
            content += (
                f" Destination {destination['name']} in {destination['location']}. "
                f"Description: {destination['description']} Activities:\n- {activities} "
            )

        print(f"[tool] vacation_lookup destination_results={len(destinations)}")
        return content

    ships = travel.similarity_search(input)

    content = ""
    for ship in ships:
        amenities = "\n- ".join(ship.amenities)
        content += (
            f" Cruise ship {ship.name} description: {ship.description} "
            f"with amenities {amenities} "
        )

    print(f"[tool] vacation_lookup ship_results={len(ships)}")
    return content

@tool
def itinerary_lookup(ship_name:str) -> str:
    """find ship itinerary, cruise packages and destinations by ship name"""

    print(f"[tool] itinerary_lookup ship_name={ship_name}")

    it = travel.itnerary_search(ship_name)
    results = ""

    for i in it:
        rooms = "\n- ".join(i.Rooms)
        schedule = "\n- ".join(i.Schedule)
        results += (
            f" Cruise Package {i.Name} room prices: {rooms} "
            f"schedule: {schedule}"
        )

    print(f"[tool] itinerary_lookup results={len(it)}")
    return results


@tool
def book_cruise(package_name:str, passenger_name:str, room: str )-> str:
    """book cruise using package name and passenger name and room """
    print(f"[tool] book_cruise package={package_name} passenger={passenger_name} room={room}")

    # LLM defaults empty name to John Doe 
    if passenger_name == "John Doe":
        return "In order to book a cruise I will need to know your name."
    else:
        if room == '':
            return "which room would you like to book"            
        return "Cruise has been booked, ref number is 343242"