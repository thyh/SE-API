from sgqlc.endpoint.http import HTTPEndpoint
import json
import os
import ftplib
import requests

url = 'https://prod.sparrow.escapes.tech/graphql'
headers = {'Accept': 'application/json'}

query = """
{
  sales(affiliate: "es") {
    sales_id:id
    sales_type:type
    dates {
      dates_start:start
      dates_end:end
    }
    location {
      location_city:city {location_city_name:name}
      location_country:country{location_country_name: name}
      location_continent:continent{location_continent_name:name}
      location_division:division{location_division_name:name}
      location_latitude:latitude
      location_longitude:longitude
    }
    prices{
			prices_discount:discount
      prices_leadRate:leadRate{
        prices_leadRate_forDisplay:forDisplay
      }
    }
    links {
      links_sale:sale
    }
  }
}
"""
variables = {'varName': 'value'}

endpoint = HTTPEndpoint(url, headers)
data = endpoint(query, variables)

# write JSON data
filename = "uk.sales.json"
with open(filename, "w") as output_file:
    json.dump(list(data.values()), output_file, indent=4)

# uploads to FTP
file = open(filename,"rb")
from ftplib import FTP
ftp = ftplib.FTP('ftp.gridhost.co.uk')
ftp.login (os.environ.get('FEEDFTPUSER'),os.environ.get('FEEDFTPPASS'))
#ftp.login ('feed@lp.secretescapes.com','pH!c86!PY2uZ@jk')
ftpResponse = str(ftp.storbinary('STOR /gq/' + filename, file, 1))
file.close()

# Set the webhook_url to the one provided by Slack when you create the webhook at https://my.slack.com/services/new/incoming-webhook/
webhook_url = 'https://hooks.slack.com/services/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'
slack_data = {'text': ":uk: *UK JSON feed* uploaded: " + ftpResponse}

response = requests.post(
    webhook_url, data=json.dumps(slack_data),
    headers={'Content-Type': 'application/json'}
)
if response.status_code != 200:
    raise ValueError(
        'Request to slack returned an error %s, the response is:\n%s'
        % (response.status_code, response.text)
    )

