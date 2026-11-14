
import random

from faker import Faker

from .config import SEED
from datetime import datetime, timezone

# Shared deterministic random generator
rng = random.Random(SEED)

# Shared Faker instance
fake = Faker("en_IN")
Faker.seed(SEED)
fake.seed_instance(SEED)


def random_choice(values):
    return rng.choice(values)


def random_integer(minimum, maximum):
    return rng.randint(minimum, maximum)


def random_boolean(probability=0.5):
    return rng.random() < probability


def random_decimal(minimum, maximum):
    return round(rng.uniform(minimum, maximum), 2)


def random_datetime(start, end):
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    return fake.date_time_between(
        start_date=start_date,
        end_date=end_date,
        tzinfo=timezone.utc
    )


def random_name():
    return fake.name()


def random_email():
    return fake.email()


def random_phone():
    return fake.phone_number()

def random_weighted_choice(options):
    """
    Select a value based on its assigned probability.

    Example:
    {"STANDARD": 0.60, "GOLD": 0.10}
    """
    return rng.choices(
        population=list(options.keys()),
        weights=list(options.values()),
        k=1
    )[0]
def random_sample(values, count):
    return rng.sample(values, count)
