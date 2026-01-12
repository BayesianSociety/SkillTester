import os
import requests
import sys

DEFAULT_CIK = "0002012383"


def get_latest_13f_url(cik: str) -> str | None:
    # Pad CIK to 10 digits
    cik_padded = str(cik).zfill(10)
    headers = {"User-Agent": "MyExplorer biuro.fundation@gmail.com"}

    # Get all submissions
    url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
    data = requests.get(url, headers=headers, timeout=30).json()

    recent_filings = data["filings"]["recent"]

    # Find the most recent 13F-HR
    for i, form in enumerate(recent_filings["form"]):
        if form == "13F-HR":
            accession = recent_filings["accessionNumber"][i]
            acc_no_dashes = accession.replace("-", "")

            # Construct the direct .txt link
            final_url = (
                "https://www.sec.gov/Archives/edgar/data/"
                f"{int(cik)}/{acc_no_dashes}/{accession}.txt"
            )
            return final_url
    return None


def main() -> int:
    cik = os.environ.get("CIK") or (sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CIK)
    result = get_latest_13f_url(cik)
    print(result)

    with open("output.txt", "w", encoding="utf-8") as f:
        if result:
            f.write(result + "\n")
        else:
            f.write("No 13F-HR filing found.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
