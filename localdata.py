import os
import xml.etree.ElementTree as ET
import csv
import tempfile
import urllib.request
import zipfile

fields ={"bplcNm": "", "siteWhlAddr": "", "apvPermYmd": "", "upjong": "", "uptaeNm": ""}
hangul_fields = ["업소명", "주소", "사업자등록일", "업종", "업태"]

def parses_and_write_csv(directory, csvfile):
    csv_writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
    rows = []

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
        rows.extend(datas)
    return rows

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
    output_file = os.path.join("static", "output.csv")
    localdata_path = tempfile.TemporaryDirectory()
    #print(localdata_path.name)

    # download localdata
    download_localdata(url, extract_path=localdata_path.name)

    sheet = []
    # write csv
    with open(output_file, 'w', newline='') as csvfile:
        rows = parses_and_write_csv(localdata_path.name, csvfile)
        sheet.extend(rows)
    localdata_path.cleanup()

    # add hangul header
    hangul_header = ",".join(hangul_fields)
    line_prepender(output_file, hangul_header)

    return sheet[:20]
    #return output_file

if __name__ == '__main__':
    date =''
    location =''
    output_file = filter_localdata(date, location)
