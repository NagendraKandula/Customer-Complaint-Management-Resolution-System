
from data_generation.config import (
    DATASET_SIZE,
    SCALE,
    BATCH_SIZE,
)

from data_generation.random_utils import (
    random_decimal,
    random_boolean,
)

from data_generation.id_generator import id_generator


# Product catalogue:
# (product_name, minimum_price, maximum_price, is_safety_critical)

PRODUCT_CATALOGUE = {
    "Electronics": [
        ("Smartphone", 8000, 80000, False),
        ("Laptop", 25000, 150000, False),
        ("Tablet", 8000, 60000, False),
        ("Bluetooth Speaker", 500, 10000, False),
        ("Wireless Earbuds", 500, 12000, False),
        ("Smart Watch", 1000, 25000, False),
        ("Power Bank", 500, 5000, True),
        ("Mobile Charger", 200, 2500, True),
        ("USB Cable", 100, 1000, False),
        ("LED Monitor", 5000, 40000, False),
        ("Keyboard", 300, 5000, False),
        ("Computer Mouse", 150, 3000, False),
        ("WiFi Router", 1000, 8000, False),
        ("External Hard Drive", 3000, 15000, False),
        ("USB Flash Drive", 200, 2000, False),
        ("Webcam", 500, 8000, False),
        ("Gaming Console", 15000, 60000, False),
        ("Graphics Tablet", 2000, 20000, False),
        ("Lithium Battery Pack", 1000, 10000, True),
        ("Extension Board", 300, 3000, True),
    ],

    "Home Appliances": [
        ("Refrigerator", 12000, 80000, False),
        ("Washing Machine", 10000, 60000, False),
        ("Microwave Oven", 5000, 30000, False),
        ("Electric Kettle", 500, 4000, True),
        ("Room Heater", 1000, 8000, True),
        ("Air Conditioner", 25000, 80000, False),
        ("Ceiling Fan", 1000, 8000, False),
        ("Table Fan", 500, 4000, False),
        ("Mixer Grinder", 1000, 10000, True),
        ("Induction Cooktop", 1000, 6000, True),
        ("Vacuum Cleaner", 2000, 20000, False),
        ("Water Purifier", 5000, 30000, False),
        ("Air Purifier", 5000, 40000, False),
        ("Rice Cooker", 1000, 6000, True),
        ("Toaster", 500, 5000, True),
        ("Dishwasher", 20000, 80000, False),
        ("Water Geyser", 4000, 25000, True),
        ("Electric Iron", 500, 5000, True),
        ("Room Humidifier", 1000, 10000, False),
        ("Food Processor", 2000, 15000, False),
    ],

    "Personal Care": [
        ("Hair Dryer", 500, 5000, True),
        ("Electric Trimmer", 500, 5000, True),
        ("Electric Shaver", 800, 8000, True),
        ("Hair Straightener", 500, 6000, True),
        ("Hair Curler", 700, 7000, True),
        ("Electric Toothbrush", 500, 5000, True),
        ("Digital Weighing Scale", 300, 3000, False),
        ("Facial Cleansing Brush", 300, 3000, False),
        ("Massage Gun", 1500, 12000, False),
        ("Heating Pad", 500, 4000, True),
        ("Blood Pressure Monitor", 1000, 6000, False),
        ("Digital Thermometer", 200, 1500, False),
        ("Foot Massager", 2000, 15000, False),
        ("Water Flosser", 800, 6000, False),
        ("Nail Care Kit", 300, 3000, False),
    ],

    "Furniture": [
        ("Office Chair", 2000, 20000, False),
        ("Study Table", 2000, 15000, False),
        ("Bookshelf", 1500, 12000, False),
        ("Dining Table", 5000, 40000, False),
        ("Sofa", 10000, 80000, False),
        ("Bed Frame", 5000, 50000, False),
        ("Mattress", 3000, 40000, False),
        ("Wardrobe", 5000, 50000, False),
        ("Coffee Table", 1000, 10000, False),
        ("TV Stand", 1500, 12000, False),
        ("Side Table", 500, 5000, False),
        ("Recliner Chair", 8000, 50000, False),
        ("Shoe Rack", 800, 6000, False),
        ("Baby Crib", 3000, 25000, True),
        ("Storage Cabinet", 1500, 15000, False),
    ],

    "Accessories": [
        ("Laptop Bag", 500, 5000, False),
        ("Phone Case", 100, 2000, False),
        ("Screen Protector", 50, 1000, False),
        ("Laptop Stand", 300, 3000, False),
        ("Headphone Stand", 200, 2000, False),
        ("Camera Tripod", 500, 5000, False),
        ("Travel Adapter", 200, 2000, True),
        ("Surge Protector", 500, 4000, True),
        ("HDMI Cable", 100, 1500, False),
        ("Wireless Presenter", 500, 3000, False),
        ("Smart Watch Strap", 100, 1500, False),
        ("Camera Lens", 3000, 50000, False),
        ("Microphone", 500, 15000, False),
        ("Laptop Cooling Pad", 500, 4000, False),
        ("Memory Card", 200, 5000, False),
    ],

    "Other": [
        ("Water Bottle", 100, 1500, False),
        ("Backpack", 500, 5000, False),
        ("Wall Clock", 200, 3000, False),
        ("Desk Lamp", 300, 4000, False),
        ("Torch Light", 200, 3000, False),
        ("Kitchen Storage Set", 300, 3000, False),
        ("Non-stick Cookware Set", 1000, 10000, False),
        ("Dinner Set", 500, 5000, False),
        ("Electric Sewing Machine", 5000, 25000, True),
        ("Portable Generator", 10000, 80000, True),
        ("Smoke Detector", 500, 5000, False),
        ("Fire Extinguisher", 1000, 8000, False),
        ("Garden Water Pump", 2000, 15000, True),
        ("Digital Safe", 3000, 25000, False),
        ("Air Mattress", 1000, 8000, False),
    ],
}


def generate_product_records():
    """
    Generate the product catalogue in memory.
    """

    total_products = round(
        DATASET_SIZE["products"]
    )

    all_products = []

    for category, products in PRODUCT_CATALOGUE.items():

        for product in products:
            all_products.append((category, product))

    if total_products > len(all_products):
        raise ValueError(
            f"Requested {total_products} products, "
            f"but catalogue contains only {len(all_products)}."
        )

    records = []

    for category, product in all_products[:total_products]:

        product_name, min_price, max_price, safety_critical = product

        product_id = id_generator.product_id()

        unit_price = random_decimal(
            min_price,
            max_price
        )

        is_active = random_boolean(0.98)

        records.append((
            product_id,
            product_name,
            category,
            unit_price,
            safety_critical,
            is_active,
        ))

    return records


def insert_products(connection, products):
    """
    Insert products using multi-row INSERT statements.
    """

    cursor = connection.cursor()

    columns = 6

    try:
        print("Checking existing products...", flush=True)

        cursor.execute("SELECT COUNT(*) FROM products")
        existing_count = cursor.fetchone()[0]

        print("Existing products:", existing_count, flush=True)

        if existing_count > 0:
            raise RuntimeError(
                f"Products table already contains {existing_count} "
                "records. Refusing to insert duplicates."
            )

        total = len(products)

        for start in range(0, total, BATCH_SIZE):

            batch = products[start:start + BATCH_SIZE]

            row_placeholder = "(" + ", ".join(
                ["%s"] * columns
            ) + ")"

            placeholders = ", ".join(
                [row_placeholder] * len(batch)
            )

            insert_query = f"""
                INSERT INTO products (
                    product_id,
                    product_name,
                    product_category,
                    unit_price,
                    is_safety_critical,
                    is_active
                )
                VALUES {placeholders}
            """

            parameters = [
                value
                for product in batch
                for value in product
            ]

            cursor.execute(insert_query, parameters)

            print(
                f"Inserted {min(start + len(batch), total)} "
                f"/ {total} products",
                flush=True
            )

        connection.commit()

        print("\nProduct data inserted successfully!")
        print("Total products:", total)

    except Exception:
        connection.rollback()
        print("Product insertion failed. Transaction rolled back.")
        raise

    finally:
        cursor.close()


def run_product_generation(connection):
    print("Generating product records...", flush=True)

    products = generate_product_records()

    print("Generated records:", len(products), flush=True)

    insert_products(connection, products)
