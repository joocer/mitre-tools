from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
from datetime import datetime

attack_url = r"https://github.com/mitre/cti/blob/master/enterprise-attack/enterprise-attack.json?raw=true"
capec_url  = r"https://raw.githubusercontent.com/mitre/cti/master/capec/stix-capec.json"
cwe_url    = r'https://cwe.mitre.org/data/csv/2000.csv.zip'
nvd_url    = r'https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-{year}.json.zip'

# asvs is OWASP, not MITRE
asvs_url   = r'https://raw.githubusercontent.com/OWASP/ASVS/master/4.0/OWASP%20Application%20Security%20Verification%20Standard%204.0-en.csv'


def download_file(url, savelocation):
    resp = urlopen(url)
    f = open(savelocation, 'w', errors='ignore')
    f.write(resp.read().decode('utf8', errors='backslashreplace'))
    f.close()

def download_zip(url, savelocation, encoding='utf-8'):
    resp = urlopen(url)
    zipfile = ZipFile(BytesIO(resp.read()))
    for file in zipfile.namelist():
        f = open(savelocation, 'wb')
        for line in zipfile.open(file).readlines():
            text = line
            #text = line.decode(encoding)
            #text = str(line)[2:-1]
            #text = replace_last(text, '\\r\\n', '')
            f.write(text)
        f.close()

# NVD files need some logic to get them all
def download_nvd_files():
    currentYear = datetime.now().year
    filepath = r'data/raw/nvdcve-1.1-{year}.json'
    for year in range(2002, currentYear + 1):
        print ('downloading NVD file for year', year)
        download_zip(nvd_url.replace('{year}', str(year)), filepath.replace('{year}', str(year)), 'mbcs')

def download_exploit_db(savelocation):
    # ExploitDB Reference Map
    import pandas as pd
    edb = pd.read_html('https://cve.mitre.org/data/refs/refmap/source-EXPLOIT-DB.html')
    edb = edb[3] # it's the forth table on the page
    edb.to_csv(savelocation,index=False)
    print('done')

# support functions, not core functionality
def replace_last(source_string, replace_what, replace_with):
    head, _sep, tail = source_string.rpartition(replace_what)
    return head + replace_with + tail

print('starting downloads')
download_file(attack_url, r'data/raw/enterprise-attack.json')
print('downloaded ATT&CK')
download_file(capec_url, r'data/raw/stic-capec.json')
print('downloaded CAPEC')
download_zip(cwe_url, r'data/raw/2000-cwe.csv', 'iso-8859-1')
print('downloaded CWE')
download_nvd_files()
print('downloaded CVE')
download_exploit_db(r'data/raw/mitre-exploitdb.csv')
print('downloaded exploit db')
download_file(asvs_url, r'data/raw/OWASP Application Security Verification Standard 4.0-en.csv')
print('done')