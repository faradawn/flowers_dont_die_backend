import requests

def fetch_leetcode_data(slug):
    base_url = "https://alfa-leetcode-api.onrender.com/select"
    params = {"titleSlug": slug}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
slug = "two-sum"  # Replace with the desired problem slug
result = fetch_leetcode_data(slug)

if result:
    print(f"Data for {slug}:")
    print(result)
else:
    print("Failed to fetch data.")