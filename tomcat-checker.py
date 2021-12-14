#!/usr/bin/env python3

from html.parser import HTMLParser
from pkg_resources import parse_version
import re, urllib.request, json, os, argparse, ssl

# get url content & html version parser from tomcat repo

def getUrlContent(url):
  ctx = ssl.create_default_context()
  ctx.check_hostname = False
  ctx.verify_mode = ssl.CERT_NONE
  try:
    fp = urllib.request.urlopen(url, context=ctx)
    mybytes = fp.read()
    fp.close()
    return mybytes.decode("utf8")
  except urllib.error.HTTPError:
    return '{"tags": []}'
  

class CustomHTMLParser(HTMLParser):
  def __init__(self) -> None:
    self.versionlist = []
    super().__init__()
  
  def __call__(self, html):
    self.feed(html)
    return self.versionlist

  def handle_data(self, data):
    if re.match(r"^v[0-9]+\.[0-9]+\.[0-9]+", data):
      self.versionlist.append(data[1:-1])

# -----------------
# script arguments

argparser = argparse.ArgumentParser(description='Tomcat version check script')
argparser.add_argument('--registryUrl', default='https://registry:5000')
argparser.add_argument('--registryImage', default='tomcat')
argparser.add_argument('--outputEnvFile', default='update.env')
argparser.add_argument('--forceUpdate', action='store_true')
scriptArgs = argparser.parse_args()

tomcatImage = scriptArgs.registryImage
registryUrl = scriptArgs.registryUrl
outputEnvFile = scriptArgs.outputEnvFile
forceUpdate = scriptArgs.forceUpdate

# getting versions available to download
parser = CustomHTMLParser()
availableVersionList = parser(
  getUrlContent("https://apache-mirror.rbc.ru/pub/apache/tomcat/tomcat-9/")
)

# find latest version from apache mirror
latestAvailableVersion = max(availableVersionList, key=lambda x: parse_version(x), default="0")

# getting versions from registry
registryVersionList = json.loads(
  getUrlContent(f"{registryUrl}/v2/{tomcatImage}/tags/list")
)['tags']

# find latest version from registry
latestRegistryVersion = max(registryVersionList, key=lambda x: parse_version(x), default="0")

# default values to .env file
ENV_IMAGE_NEED_UPDATE = 'False'
ENV_IMAGE_UPDATE_VERSION = latestRegistryVersion
ENV_IMAGE_DOWNLOAD_URL = f"https://apache-mirror.rbc.ru/pub/apache/tomcat/tomcat-9/v{ENV_IMAGE_UPDATE_VERSION}/bin/apache-tomcat-{ENV_IMAGE_UPDATE_VERSION}.tar.gz"

# compare latests...
if not forceUpdate and (parse_version(latestAvailableVersion) <= parse_version(latestRegistryVersion)):
  print(f"""No update needed
------------
Image: {tomcatImage}
Current Tomcat version is latest: {latestRegistryVersion}""")

else:
  ENV_IMAGE_NEED_UPDATE = 'True'
  ENV_IMAGE_UPDATE_VERSION = latestAvailableVersion
  ENV_IMAGE_DOWNLOAD_URL = f"https://apache-mirror.rbc.ru/pub/apache/tomcat/tomcat-9/v{ENV_IMAGE_UPDATE_VERSION}/bin/apache-tomcat-{ENV_IMAGE_UPDATE_VERSION}.tar.gz"
  print(f"""Update needed
------------
Image: {tomcatImage}
Current latest registry Tomcat version: {latestRegistryVersion}
Current latest available Tomcat version: {latestAvailableVersion}""")

# write .env file
envFileString = f"IMAGE_NEED_UPDATE={ENV_IMAGE_NEED_UPDATE}\nIMAGE_UPDATE_VERSION={ENV_IMAGE_UPDATE_VERSION}\nIMAGE_DOWNLOAD_URL={ENV_IMAGE_DOWNLOAD_URL}"
f = open(outputEnvFile, 'w')
f.write(envFileString)
f.close()

print(f"""------------
Now you can use "./{outputEnvFile}" file to decide what to do next.
It contents the following lines:
{envFileString}""")