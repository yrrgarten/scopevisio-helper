# Document Export Helper for Scopevisio

## Preamble

Scopevisio AG provides a "Business Automation Platform" which includes
a Finance module and a DMS. We used the Finance module for accounting
purposes together with the DMS for a completely digital accounting workflow.

We needed to backup the entire system recently and ran into a few 
obstacles. While exporting the accouting data for straightforward, getting
the documents from the DMS was a bit of a challenge. The built-in exporting
capabilities are pretty limited. First, it is difficult to export a large
number of documents at a time. Secondly, the exported document do not carry
or maintain any reference to the associated bookings. So you end up with a 
high number of pdf without linkage to the booking entries.

Fortunately, Scopevision provides a REST API ("OpenScope") which allows
fetching the documents programmatically.

The script is "hacky" - use on your own risk.

## Scopevisio Document Export Script

### Requirements
The script is written in Python 3 and make use of [requests](https://docs.python-requests.org/en/latest/) 
and [pandas](https://pandas.pydata.org/) which might need to be installed separately.

### Authentification
For communicating with the API endpoints we obviouolsy need to be authorized.
A Bearer token needs to be send with every request which needs to be obtained by
authentificating against the `token` endpoint as described in the [documentation](https://appload.scopevisio.com/static/browser/index.html#!/documentation).

I did not implement the OAuth2 workflow in my script, but rather used the Swagger 
resource provided by Scopevisio for authentificating and copied the auth code from there
into my script. This works good enough for this purpose as the token seems to have a rather
long lifetime. A token refresh was not required in my scenario.

### Description and Usage
After authtentificating and getting authorization, the Bearer token needs to be copied
to the script to the `ACCESS_TOKEN` variable.

The `FY` variable needs to be set to the financial year which shall be exported.

The scripts get all documents for the given year and saves them in a `{YEAR}/{PERIOD}` 
directory structure in the working directory.

The filenames correspond to the Journal Entry ID which allows associating the documents
with the bookings.

Logging is enabled and output is written to `export.log` in the same directory.

The script can certainly be improved and extended, e.g.
* error handling
* OAuth flow
* providing the YEAR as argument
* ...

### Links

* General Documentation: https://appload.scopevisio.com/static/browser/index.html#!/documentation
* Swagger: https://appload.scopevisio.com/static/swagger/index.html
