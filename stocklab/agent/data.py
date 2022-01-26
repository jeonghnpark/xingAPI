import requests
import configparser

import xml.etree.ElementTree as ET


class Data():
    CORP_CODE_URL = 'http://api.seibro.or.kr/openapi/service/CorpSvc/getIssucoCustnoByNm'
