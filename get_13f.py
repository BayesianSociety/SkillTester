import requests

def get_latest_13f_url(cik):
    # Pad CIK to 10 digits
    cik_padded = str(cik).zfill(10)
    headers = {'User-Agent': 'MyExplorer biuro.fundation@gmail.com'}
    
    # Get all submissions
    url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
    data = requests.get(url, headers=headers).json()
    
    recent_filings = data['filings']['recent']
    
    # Find the most recent 13F-HR
    for i, form in enumerate(recent_filings['form']):
        if form == '13F-HR':
            accession = recent_filings['accessionNumber'][i]
            acc_no_dashes = accession.replace('-', '')
            
            # Construct the direct .txt link
            final_url = (
                f"https://www.sec.gov/Archives/edgar/data/"
                f"{int(cik)}/{acc_no_dashes}/{accession}.txt"
            )
            return final_url
    return None


# Example Use
result = get_latest_13f_url("0002012383")
print(result)

with open("output.txt", "w") as f:
    if result:
        f.write(result + "\n")
    else:
        f.write("No 13F-HR filing found.\n")

