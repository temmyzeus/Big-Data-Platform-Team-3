import pandas as pd


def generate_data(data_gen_func, num_rows, output_path):
    """
    Generate data using the provided function and number of rows.
    """
    data = [
        data_gen_func()
        for _ in range(num_rows)
    ]
    df = pd.DataFrame(data)
    df.to_parquet(output_path, index=False)
    return output_path
