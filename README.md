# get-pypi-metadata
Python3 script to query Snyk for PyPi package metadata by looping 
`package_name`s in `requirements.txt` and requesting
`https://snyk.io/advisor/python/{package_name}`.

It's super simple, works today (March 6, 2025), maybe not tomorrow. 

I won't maintain it, but it fitted my use case and sharing in case it also 
fits someone else their use case. 
