import requests


def fetch_and_extract(filing_url: str):
    headers = {'User-Agent': 'MyExplorer biuro.fundation@gmail.com'}
    resp = requests.get(filing_url, headers=headers, timeout=30)
    resp.raise_for_status()

    fields = {
        "Company Conformed Name": None,
        "Conformed period of report": None,
    }

    for line in resp.text.splitlines():
        stripped = line.strip()
        upper = stripped.upper()

        if upper.startswith("COMPANY CONFORMED NAME"):
            fields["Company Conformed Name"] = stripped.split(":", 1)[-1].strip()
        elif upper.startswith("CONFORMED PERIOD OF REPORT"):
            fields["Conformed period of report"] = stripped.split(":", 1)[-1].strip()

        if all(fields.values()):
            break

    return fields


def read_filing_url_from_file(filename="output.txt"):
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                return line
    raise ValueError("output.txt does not contain a valid filing URL")


if __name__ == "__main__":
    data = fetch_and_extract(read_filing_url_from_file())
    for label, value in data.items():
        print(f"{label}: {value}")

