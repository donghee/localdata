import os
import xml.etree.ElementTree as ET
import csv
import tempfile
import urllib.request
import zipfile
import ssl
import logging

ssl._create_default_https_context = ssl._create_unverified_context

# 로거 설정
logging.basicConfig(filename='localdata.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

fields ={"bplcNm": "", "siteWhlAddr": "", "apvPermYmd": "", "upjong": "", "uptaeNm": ""}
hangul_fields = ["업소명", "주소", "사업자등록일", "업종", "업태"]
output_file = os.path.join("static", "output.csv")

def parses_and_write_csv(directory, csvfile):
    csv_writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')

    for xml_file in os.listdir(directory):
        xml_data = open(os.path.join(directory, xml_file), "r").read()
        upjong = xml_file.split(".")[0].split("_")[5]
        root = ET.fromstring(xml_data)
        datas = []
        for row in root.findall("./body/rows/row"):
            data = {}
            for child in row:
                if (child.tag == "bplcNm" or child.tag == "siteWhlAddr" or child.tag == "apvPermYmd" or child.tag == "uptaeNm" or child.tag == "apvPermYmd"):
                    data[child.tag] = child.text
                data["upjong"] = upjong
            #print(data)
            datas.append(data)
        csv_writer.writerows(datas)

def line_prepender(filename, line):
    with open(filename, 'r+') as csvfile:
        content = csvfile.read()
        csvfile.seek(0, 0)
        csvfile.write(line.rstrip('\r\n') + '\n' + content)

def download_localdata(url, extract_path="/tmp/LOCALDATA_NOWMON_XML"):
    filename = tempfile.NamedTemporaryFile()
    #print(filename.name)
    urllib.request.urlretrieve(url, filename.name)

    with zipfile.ZipFile(filename, 'r') as zip_ref:
        for info in zip_ref.infolist():
            info.filename = info.filename.encode('cp437').decode('euc-kr')
            zip_ref.extract(info, extract_path)

    filename.close()

def filter_localdata(date, location):
    url = "https://www.localdata.go.kr/datafile/LOCALDATA_NOWMON_XML.zip"
    localdata_path = tempfile.TemporaryDirectory()
    #print(localdata_path.name)

    # download localdata
    download_localdata(url, extract_path=localdata_path.name)

    # write csv
    with open(output_file, 'w', newline='', encoding='UTF-8') as csvfile:
        parses_and_write_csv(localdata_path.name, csvfile)
    localdata_path.cleanup()

    # add hangul header
    hangul_header = ",".join(hangul_fields)
    line_prepender(output_file, hangul_header)

    return output_file

def paginate_localdata(localdata_file, page_number, location='', start='', end=''):
    rows = []
    try: 
        with open(localdata_file, newline='') as csvfile:
            next(csvfile) # skip header
            reader = csv.DictReader(csvfile, fieldnames=fields)
            for row in reader:
                rows.append(row)
    except Exception as e:
        logging.error(f"CSV file read error (column {reader.line_num}): {e}")

    if location:
        rows = [row for row in rows if row["siteWhlAddr"].startswith(location)] 

    # TODO check date format
    if start:
        rows = [row for row in rows if row["apvPermYmd"] >= start] 
    if end:
        rows = [row for row in rows if row["apvPermYmd"] <= end] 
    rows = sorted(rows, key=lambda x: x["apvPermYmd"], reverse=True)

    page_count = len(rows) // 20
    return page_count, rows[(page_number-1)*20:page_number*20]

if __name__ == '__main__':
    date =''
    location =''
    output_file = filter_localdata(date, location)
