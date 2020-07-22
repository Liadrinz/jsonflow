import json

import jsonflow.config as conf
from jsonflow.core import jf

counter = 0

def handle_result(result):
    global counter
    counter += 1

@jf.thread(callback=handle_result)
@jf.src(
    url='http://api-mall-admin-test.idc.yst.com.cn/ecu-mall-admin/commodity/commodities:query',
    method='post',
    consumes='application/json',
    data='''{
        "skuId": "",
        "statuses": [],
        "commodityName": "",
        "skuCategoryIds": [],
        "brandIds": [],
        "spuId": "",
        "isCombine": null,
        "supplierIds": [],
        "deliveryTypes": [],
        "areaExist": "",
        "pageIndex": <pageIndex>,
        "pageSize": <pageSize>
    }'''
)
@jf.flow(
    json.loads,
    lambda result: result['data']
)
def query_commodities(pageIndex, pageSize):
    return jf.data

if __name__ == "__main__":
    ps = []
    for i in range(5):
        query_commodities(pageIndex=i + 1, pageSize=20)
    jf.wait()
    print(counter)