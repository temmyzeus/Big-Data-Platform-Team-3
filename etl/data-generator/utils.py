from datetime import datetime
import random
import uuid

from faker import Faker
from faker_vehicle import VehicleProvider

from choices import Listing

fake = Faker()
fake.add_provider(VehicleProvider)

fake_be = Faker(
    locale=["nl_BE", "fr_BE"] # French Belgium, Dutch Belgium & German Belgium Data (Locale Not Available)
)


def generate_listing():
    id_ = int(str(uuid.uuid4().int)[:8])
    vehicle_object: dict[str, int | str] = fake.vehicle_object()
    make = vehicle_object["Make"]
    model = vehicle_object["Model"]
    year = vehicle_object["Year"]
    is_used = random.choice([True, False])
    if is_used:
        mileage = random.randint(5_000, 150_000) # Total distance the car has traveled in KM
        condition = random.choice(Listing.conditions["used"])
    else:
        mileage = random.randint(0, 200) # Total distance the car has traveled in KM
        condition = random.choice(Listing.conditions["new"])
    category = vehicle_object["Category"]
    base_price = max(2000, 50000 - ((datetime.now().year - year) * 1000) - (mileage * 0.05))
    price = round(random.uniform(base_price * 0.9, base_price * 1.1), 2)
    
    return {
        "listing_id": id_,
        "vehicle_id": f"V{id_}",
        "seller_id": f"S{random.randint(1, 2000)}",
        "make": make,
        "model": model,
        "year": year,
        "price": price,
        "category": category,
        "is_used": is_used,
        "listing_date": fake.date_between(start_date='-2y', end_date='today').strftime("%Y-%m-%d"),
        "status": random.choice(Listing.statuses),
        "location": fake_be.city(),
        "mileage": mileage,
        "condition": condition,
        "is_featured": random.choice([True, False]),
        "seller_type": random.choice(Listing.seller_types)
    }

