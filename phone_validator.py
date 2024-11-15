import requests
import phonenumbers
from phonenumbers import geocoder

API_KEY = "allah" 
BASE_URL = "http://apilayer.net/api/validate"

carrier_email_domains = {
    "AT&T": "@txt.att.net",
    "Verizon": "@vtext.com",
    "T-Mobile": "@tmomail.net",
    "Sprint": "@messaging.sprintpcs.com",
    "Boost Mobile": "@myboostmobile.com",
    "Cricket Wireless": "@sms.cricketwireless.net",
    "MetroPCS": "@mymetropcs.com",
    "Telstra": "@telstra.com.au",
    "Optus": "@optusnet.com.au",
    "Vodafone": "@vodafone.com.au",
}

def get_email_gateway(carrier_name):
    for carrier, domain in carrier_email_domains.items():
        if carrier.lower() in carrier_name.lower():
            return domain
    return None

def validate_phone_number(phone_number):
    try:
       
        parsed_number = phonenumbers.parse(phone_number, None)
        country_code = geocoder.region_code_for_number(parsed_number)  
        local_number = str(parsed_number.national_number)  
        
        url = f"{BASE_URL}?access_key={API_KEY}&number={local_number}&country_code={country_code}&format=1"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if data.get("valid") and data.get("line_type") == "mobile":
                carrier = data.get("carrier", "").strip()
                email_gateway = get_email_gateway(carrier)
                if email_gateway:
                    return {"valid": True, "email_gateway": f"{local_number}{email_gateway}"}
                else:
                    return {"valid": True, "email_gateway": phone_number, "reason": "Carrier email domain not found"}
            else:
                return {"valid": False, "number": phone_number, "reason": "Not a valid mobile number"}
        else:
            return {"valid": False, "number": phone_number, "reason": f"API Error: {response.status_code}"}

    except phonenumbers.phonenumberutil.NumberParseException:
        return {"valid": False, "number": phone_number, "reason": "Invalid number format"}
    
def process_phone_numbers(input_file, valid_output_file, invalid_output_file):
    with open(input_file, 'r') as f:
        phone_numbers = [line.strip() for line in f.readlines()]

    with open(valid_output_file, 'w') as valid_file, open(invalid_output_file, 'w') as invalid_file:
        for phone_number in phone_numbers:
            result = validate_phone_number(phone_number)

            if result:
                if result["valid"]:
                    valid_file.write(f"{result['email_gateway']}\n")
                else:
                    invalid_file.write(f"Invalid number: {result['number']} ({result['reason']})\n")

input_file = "AUPhone.txt"
valid_output_file = "valid_numbers.txt"
invalid_output_file = "invalid_numbers.txt"

process_phone_numbers(input_file, valid_output_file, invalid_output_file)
