import random
import uuid
from multiprocessing import Pool, cpu_count

# import boto3
import pandas as pd
from faker import Faker
from faker_vehicle import VehicleProvider
from tqdm import tqdm

fake = Faker()
fake.add_provider(VehicleProvider)


def generate_car_sales_data(batch_size) -> list:
    data = []

    for _ in range(batch_size):

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


def make_data_into_df(data: list):
    return pd.DataFrame(data)


def save_data_into_parquet(df):
    return df.to_parquet("data/car_sales_data.parquet")

# def upload_to_s3(parquet_file: str) -> None:


if __name__ == '__main__':
    TOTAL_ROWS = 100
    BATCH_SIZE = 10
    NUM_BATCHES = TOTAL_ROWS // BATCH_SIZE

    with Pool(cpu_count()) as pool:
        all_batches = list(tqdm(pool.imap(generate_car_sales_data,
                                          [BATCH_SIZE]*NUM_BATCHES),
                                total=NUM_BATCHES))

    df = make_data_into_df(all_batches)

    save_data_into_parquet(df)
