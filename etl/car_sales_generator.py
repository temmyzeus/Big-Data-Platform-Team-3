import random
import uuid

import pandas as pd
from faker import Faker
from faker_vehicle import VehicleProvider

fake = Faker()
fake.add_provider(VehicleProvider)

BATCH_SIZE = 100


def generate_car_sales_data():
    data = []

    for _ in range(BATCH_SIZE):

        data.append(
            {
                "id": str(uuid.uuid4()),
                "name": fake.name(),
                "email": f"{fake.name().lower().replace(' ', '.')}.\
                    {random.randint(1000, 9999)}@\
                        {fake.free_email_domain()}",
                "address": fake.address(),
                "phone": fake.phone_number(),
                "vehicle_year": fake.vehicle_year(),
                "vehicle_category": fake.vehicle_category(),
                "vehicle_year_make_model": fake.vehicle_year_make_model()
            }
        )
    return data


data = generate_car_sales_data()


df = pd.DataFrame(data)

df.to_parquet("data/car_sales_data.parquet")
