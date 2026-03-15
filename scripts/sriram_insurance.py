import requests

headers = {
    'sec-ch-ua-platform': '"Windows"',
    'Referer': 'https://www.shriramlife.com/download-forms',
    'api-referrer': '/download-forms',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json',
}

response = requests.get('https://www.shriramlife.com/api/v1/claim-forms/claim-centre-forms/5344', headers=headers)
print(response.json())

# https://www.shriramlife.com/api/v1/product-brochure-forms/claim-centre-forms
# https://www.shriramlife.com/api/v1/new-bussiness-forms/claim-centre-forms
# https://www.shriramlife.com/api/v1/nach-mandate-forms/claim-centre-forms

# https://www.shriramlife.com/api/v1/policy-serving-forms/claim-centre-forms/5341
# https://www.shriramlife.com/api/v1/proposal-forms/claim-centre-forms/5341
# https://www.shriramlife.com/api/v1/sb-cum-removal-forms/claim-centre-forms/5341
# https://www.shriramlife.com/api/v1/good-health-forms/claim-centre-forms/5341
# https://www.shriramlife.com/api/v1/covid-forms/claim-centre-forms/5341
# https://www.shriramlife.com/api/v1/mandatory-forms/claim-centre-forms

# https://www.shriramlife.com/api/v1/slic-handy-forms/claim-centre-forms
# https://www.shriramlife.com/api/v1/neft-forms/claim-centre-forms