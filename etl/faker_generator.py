import pandas as pd
from faker import Faker
import random
import uuid
from tqdm import tqdm

# Initialize Faker
fake = Faker()
Faker.seed(42)
random.seed(42)

from multiprocessing import Pool, cpu_count

def generate_batch(batch_size):
    """
    This is a more optimized method of generation I used as it does not generate email_id from faker as fake.unique.email() is slowing down the process due to too many scanning to confirm uniqueness.
    I have decided to use the random library for this purpose.

    """
    local_fake = Faker()
    data = []
    for _ in range(batch_size):
        name = local_fake.name()
        email = f"{name.lower().replace(' ', '.')}.{random.randint(1000, 9999)}@{local_fake.free_email_domain()}"
        address = local_fake.address().replace("\n", ", ")
        phone = local_fake.phone_number()

        company = local_fake.company()
        job = local_fake.job()
        dob = local_fake.date_of_birth(minimum_age=18, maximum_age=80)
        join_date = local_fake.date_between(start_date='-5y', end_date='today')

        data.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "address": address,
            "phone": phone,
            "company": company,
            "job_title": job,
            "date_of_birth": dob,
            "join_date": join_date
        })
    return data


if __name__ == '__main__':
    TOTAL_ROWS = 100
    BATCH_SIZE = 20
    NUM_BATCHES = TOTAL_ROWS // BATCH_SIZE

    with Pool(cpu_count()) as pool:
        all_batches = list(tqdm(pool.imap(generate_batch, [BATCH_SIZE]*NUM_BATCHES), total=NUM_BATCHES))

    final_df = pd.DataFrame([item for sublist in all_batches for item in sublist])
    final_df.drop_duplicates(subset=['name', 'email', 'date_of_birth'], inplace=True)
    final_df.to_parquet("data/realistic_data.parquet", index=False, engine="pyarrow")


