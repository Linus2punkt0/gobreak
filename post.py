import requests, random, os, mimetypes, time
from pathlib import Path

API_URL = "https://gowokegobroke.report/api/violation/upload-new-report"
MEDIA_FOLDER = "media"

def get_cookie():
    session = requests.Session()

    response = session.get(
        "https://gowokegobroke.report/api/visitor/init",
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    if response.status_code == 429:
        return False

    print("Status:", response.status_code)
    print("Cookies:", session.cookies.get_dict())
    visitor_cookie = session.cookies.get("gowogo_vt")

    if visitor_cookie:
        print("Anonymous session created!")
    else:
        print("No visitor cookie received.")
    return session.cookies.get_dict()["gowogo_vt"]


def create_session():
    session_cookie = get_cookie()
    if not session_cookie:
        return False
    session = requests.Session()
    
    # Set your own valid session cookie securely.
    session.cookies.set(
        "gowogo_vt",
        session_cookie,
        domain="gowokegobroke.report"
    )
    return session

def submit_report(file, brand_name="No Brand"):
    print(f"Uploading {file}")

    media_path = Path(f"{MEDIA_FOLDER}/{file}")

    if not media_path.exists():
        raise FileNotFoundError(f"File not found: {media_path}")

    session = create_session()
    if not session:
        print("Not able to establish session, waiting...")
        time.sleep(60 * 5)
        return False

    file_size = media_path.stat().st_size

    # Detect media type
    content_type, _ = mimetypes.guess_type(media_path.name)

    if not content_type:
        raise ValueError("Unable to determine file type")

    if content_type.startswith("video/"):
        media_type = "video"
        max_size = 10 * 1024 * 1024  # 10 MB
    elif content_type.startswith("image/"):
        media_type = "image"
        max_size = 10 * 1024 * 1024  # 10 MB
    else:
        print(f"Unsupported file type: {content_type}")
        return

    if file_size > max_size:
        print(f"{media_type.capitalize()} must be 10 MB or smaller")
        return

    print(f"Detected media type: {media_type} ({content_type})")

    # Step 1: Initialize report and obtain Azure SAS URL
    data = [
        ("FileName", media_path.name),
        ("Name", brand_name),
        ("DeclaredSize", str(file_size))
    ]

    group_id = random.randint(2, 50)
    data.append(("GroupIds", str(group_id)))

    all_tags = ["Diversity", "LGBTQP+", "Feminism", "Absurdity"]
    tag_count = random.randint(1, len(all_tags))
    selected_tags = random.sample(all_tags, tag_count)

    for tag in selected_tags:
        data.append(("Tags", tag))

    print(data)

    response = session.post(
        API_URL,
        data=data,
        timeout=30
    )

    if response.status_code == 429:
        return response
    elif response.status_code == 403:
        print("Got response 403 forbidden.")
        exit()
    upload_url = response.json()["uploadUrl"]

    print("Upload URL obtained")


    with media_path.open("rb") as media:
        upload_response = requests.put(
            upload_url,
            data=media,
            headers={
                "x-ms-blob-type": "BlockBlob",
                "Content-Type": content_type
            },
            timeout=300
        )
    return upload_response

brands = [
    "Nike", "Adidas", "Coca-Cola", "Pepsi", "McDonald's",
    "Burger King", "Starbucks", "Apple", "Samsung", "Google",
    "Microsoft", "Amazon", "Meta", "Netflix", "Disney",
    "Tesla", "Toyota", "Volkswagen", "BMW", "Mercedes-Benz",
    "Audi", "Volvo", "IKEA", "H&M", "Zara",
    "Gucci", "Prada", "Louis Vuitton", "Chanel", "Dior",
    "L'Oréal", "Dove", "Nivea", "Unilever", "Nestlé",
    "Red Bull", "Monster Energy", "Heineken", "LEGO",
    "PlayStation", "Xbox", "Nintendo", "Spotify", "Uber",
    "Airbnb", "FedEx", "DHL", "Shell", "BP", "Patagonia", "Coop",
    "Courvoisier", "DKB", "Commerzbank AG", "Primark", "HBO",
    "Michael's", "Rockstar", "Kroger", "Lidl", "Ralph Lauren", 
    "Mercedes-Benz", "Audi", "Urban Decay", "Boots UK", "Frida Baby",
    "1177", "EA", "Under Armour", "Puma", "Spotify"
]



while True:
    print("\n\n\n")
    brand = brands[random.randint(0, len(brands) - 1)]

    filename = "Bailout.png"

    filename = random.choice(os.listdir(MEDIA_FOLDER)) 

    response = submit_report(filename, brand)


    if hasattr(response, 'status_code') and response.status_code == 429:
        print("Rate limit reached. Sleeping for five minutes...")
        time.sleep(60 * 5)
        continue
    elif not response:
        print("No response received from submit_report")
        exit()
        continue

    response.raise_for_status()
    print("Azure upload successful:", response.status_code)
    print("Report successfully submitted!")
    time.sleep(5)

