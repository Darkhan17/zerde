import requests
import csv

class Parser():
    MAIN_URL ="https://ows.goszakup.gov.kz"
    URL = "/v2/contract/customer/"

    next_page_url = ""
    bin = ""
    contract_types = []
    contract_status = []
    customers = []
    suppliers = []
    trade_methods = []

    predmets = []
    def __init__(self, bin):
        self.bin = bin
        self.contract_types = self.getContractType()
        self.contract_status = self.getContractStatus()
        self.addCustomer(bin)

    def makeUrl(self):
        new_url = "no URL"
        if (self.next_page_url == ""):
            new_url = self.MAIN_URL + self.URL + self.bin
        else:
            new_url = self.MAIN_URL + self.next_page_url
        return new_url

    def makeRequest(self,url):
        headers = {"Authorization": "Bearer 1220d31d70aa17128660bff926b1bbfa", "Content-Type": "application/json"}
        response = requests.get(url, headers=headers, verify=False)
        return response


    def parse(self):
        self.write_to_file_headers()
        while(True):
            data = []
            url = self.makeUrl()
            print(url)
            response = self.makeRequest(url).json()
            self.next_page_url = response["next_page"]
            for i in response['items']:
                item = {}
                item['id'] = i['id']
                item['contract_number'] = i['contract_number']

                item['ref_contract_type'] = self.findCotractType(i['ref_contract_type_id'])

                item['ref_contract_status'] = self.findContractStatus(i['ref_contract_status_id'])
                item['crdate'] = i['crdate']
                item['contract_sum_wnds'] = i['contract_sum_wnds']
                item['customer'] = self.findCustomer(i['customer_bin'])
                item['supplier'] = self.findSupplier(i['supplier_biin'])
                item['contract_number_sys'] = i['contract_number_sys']
                item['link'] = self.getLink(item['id'])
                contract_id = i['id']
                data.append(item)
                self.parsePredmet(contract_id, item)
            if self.next_page_url == (None or ""):
                break


    def write_to_file_headers(self):
        with open("data.csv", "a", newline="") as file:
            writer = csv.DictWriter(file, ("id", "contract_number","contract_number_sys",'ref_contract_type',"ref_contract_status","crdate","contract_sum_wnds","supplier","customer","item_id", "name","quantity", "item_price", "total_sum","link"))
            writer.writeheader()
        file.close()

    def write_to_file(self,data):
        with open("data.csv", "a", newline="") as file:
            writer = csv.DictWriter(file, ("id", "contract_number","contract_number_sys",'ref_contract_type',"ref_contract_status","crdate","contract_sum_wnds","supplier","customer","item_id", "name","quantity", "item_price", "total_sum","link"))
            writer.writerows(data)
        file.close()

    def sendRequest(self,url):
        res = self.makeRequest(url).json()
        return res['items']




    ## FIND CONTRACT TYPE

    def getContractType(self):
        url = "https://ows.goszakup.gov.kz/v2/refs/ref_contract_type"
        return self.sendRequest(url)

    def findCotractType(self,id):
        for contract in self.contract_types:
            if contract['id'] == id:
                return contract['name_ru']
        return " "




    ## FIND CONTRACT STATUS INFORMATION
    def getContractStatus(self):
        url = "https://ows.goszakup.gov.kz/v2/refs/ref_contract_status"
        return self.sendRequest(url)

    def findContractStatus(self,id):
        for contract in self.contract_status:
            if contract['id'] == id:
                return contract['name_ru']






    ## FIND CUSTOMER INFORMATION
    def getCustomer(self, bin):
        url = "https://ows.goszakup.gov.kz/v2/subject/biin/" + str(bin)
        return self.makeRequest(url).json()

    def addCustomer(self, bin):
        new_customer = self.getCustomer(bin)
        self.customers.append(new_customer)
        return new_customer['name_ru']

    def findCustomer(self, bin):
        for customer in self.customers:
            if (customer['bin'] == bin):
                return [customer['name_ru']]
        return self.addCustomer(bin)




    ## FIND SUPPLIER INFORMATION
    def getSupplier(self, bin):
        url = "https://ows.goszakup.gov.kz/v2/subject/biin/" + str(bin)
        return self.makeRequest(url).json()

    def addSupplier(self, bin):
        new_supplier = self.getSupplier(bin)
        self.suppliers.append(new_supplier)
        return new_supplier['name_ru']

    def findSupplier(self, bin):
        for supplier in self.suppliers:
            if (supplier['bin'] == bin):
                return [supplier['name_ru']]
        return self.addSupplier(bin)

    ## method traiding
    def getTradeType(self):
        url = "https://ows.goszakup.gov.kz/v2/refs/ref_trade_methods"
        return self.sendRequest(url)

    def findTradeType(self, id):
        for trade in self.trade_methods:
            if trade['id'] == id:
                return trade['name_ru']
        return " "


    ## PredmetDogovora
    def getPredmet(self,id_contract):
        url = "https://ows.goszakup.gov.kz/v3/contract/" + str(id_contract) + "/units"
        return self.sendRequest(url)


    def parsePredmet(self,id_contract,item):
        data = []
        while (True):
            url = "https://ows.goszakup.gov.kz/v3/contract/" + str(id_contract) + "/units"
            response = self.makeRequest(url).json()
            next_page_url = response["next_page"]
            for i in response['items']:
                item['item_id'] = i['id']
                item['quantity'] = i['quantity']
                item['item_price'] = i['item_price_wnds']
                item['total_sum'] = i['total_sum_wnds']
                item['name'] = self.parsePlanName(i['pln_point_id'])
                data.append(item)
            if next_page_url == (None or ""):
                print(next_page_url)
                break

        self.write_to_file(data)

    def write_to_file2(self,data):
        with open("data.csv", "a", newline="") as file:
            writer = csv.DictWriter(file, (
            ))
            writer.writeheader()
            writer.writerows(data)
        file.close()




    def getPlan(self,plan_id):
        url = "https://ows.goszakup.gov.kz/v3/plans/view/" + str(plan_id)
        return self.makeRequest(url).json()

    def parsePlanName(self,plan_id):
        plan = self.getPlan(plan_id)
        return plan['name_ru'] + ' / ' + plan['name_kz']


    def getLink(self,id):
        url = 'https://www.goszakup.gov.kz/ru/egzcontract/cpublic/contract/'
        return url + str(id)


bin = input("Enter the bin of company")
parser = Parser(bin)
parser.parse()