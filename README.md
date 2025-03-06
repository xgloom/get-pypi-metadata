# get-pypi-metadata

## Usage
```
Usage: python3 get-pypi-metadata.py requirements.txt <snyk_meta.json>
```

## Info
A simple Python 3 script to fetch PyPI package metadata from Snyk by iterating over `requirements.txt` and querying:  

```
https://snyk.io/advisor/python/{package_name}
```

## Notes 
- It works today (March 6, 2025), might not tomorrow.  
- This will not be kept up-to-date; I'm just sharing this in case it helps someone else.  
