import requests

def get_currency_rates(base_currency):
    try:
        # Free endpoint from ExchangeRatesAPI.io
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"

        # Send GET request
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        # Extract currency rates
        rates = data.get('rates', {})
        if rates:
            return rates
        else:
            print("please try again.")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return {}

# Example usage
currency_rates = get_currency_rates("USD")