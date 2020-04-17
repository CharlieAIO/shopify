import threading
import json
import csv
import requests
import datetime
import time
from bs4 import BeautifulSoup
from proxymanager import ProxyManager
from dhooks import Webhook, Embed

headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
}

def get_t_name():
    threadname = threading.currentThread().getName()
    return threadname

def get_time():
    x = datetime.datetime.now()
    now = x.strftime("%X")
    return now

def loadProxy():
    proxylist = ProxyManager('proxies.txt')
    proxy = proxylist.next_proxy()
    proxies = proxy.get_dict()
    return proxies

class Main:
    def __init__(self):
        print("Welcome Back To Your Personal Shopify self.")
        self.lock = threading.Lock()
        self.menu()

    def menu(self):
        self.hook= Webhook('https://discordapp.com/api/webhooks/683601773042467018/ne0Po3j7_XO7Bn6zfPLjpjh-vCz8KLhhgYzZB3JAcW9cFWtcRcX_iWZu1Qff9bPIOW0Q')
        menuselect = input("ENTER [1] TO START TASKS |||| ENTER [0] TO CREATE A PROFILE ||| ==>")
        if menuselect == "1":
            print("STARTING ALL TASKS...")
            self.hook.send(f"**----------------------------------------**")
            self.hook.send(f"**Initiating New [SHOPIFY] Session. STARTING TASKS.**")
            self.TaskRead()
        elif menuselect == "0":
            print("PREPARING PROFILE CREATION MENU...")
            self.profileCreator()
        
    def profileCreator(self):
        prof_name =  input("  |ENTER PROFILE NAME    ===> ")
        FIRST_NAME = input("  |ENTER FIRST NAME      ===> ")
        LAST_NAME =  input("  |ENTER LAST NAME       ===> ")
        EMAIL =      input("  |ENTER EMAIL           ===> ")
        PHONE =      input("  |ENTER PHONE           ===> ")
        ADDRESS1 =   input("  |ENTER ADDRESS 1       ===> ")
        ADDRESS2 =   input("  |ENTER ADDRESS 2       ===> ")
        CITY =   input("  |ENTER CITY            ===> ")
        PROV =   input("  |ENTER PROVINCE            ===> ")
        POSTCODE =   input("  |ENTER POSTCODE        ===> ")
        COUNTRY =    input("  |ENTER COUNTRY         ===> ")
        CARDNUM =    input("  |ENTER CARD NUMBER     ===> ")
        CARDEXPM =   input("  |ENTER EXPIRY MONTH    ===> ")
        CARDEXPY =   input("  |ENTER EXPIRY YEAR     ===> ")
        CARDCVV =    input("  |ENTER CVV             ===> ")
  
        PROFILE = {"FIRST-NAME":FIRST_NAME,"LAST-NAME":LAST_NAME,"EMAIL":EMAIL,"PHONE":PHONE,"ADDRESS-1":ADDRESS1,"ADDRESS-2":ADDRESS2,"CITY":CITY,"PROVINCE":PROV,"POST-CODE":POSTCODE,"COUNTRY":COUNTRY,"CARD-NUMBER":CARDNUM,"CARD-EXP-M":CARDEXPM,"CARD-EXP-Y":CARDEXPY,"CARD-CVV":CARDCVV}
        with open(f'../PROFILES/profile_{prof_name}.json','w') as profile_in:
            json.dump(PROFILE,profile_in,indent=4)
        print("PROFILE ADDED ")
        self.menu()

    def TaskRead(self):
        with open('../tasks.csv') as tasks_csv:
            csv_reader = csv.DictReader(tasks_csv)
            for row in csv_reader:
                if row["SITE"] == "shopify":
                    u_var = row["URL/VARIANT"]
                    self.profilename= row["PROFILE"]
                    self.prox = row["PROXIES"]
                    self.size = row["SIZE"]
                    self.delay = row["DELAY"]
                    self.base = row["BASE-SITE"]
    
                    if self.prox == "YES":
                        self.useProxies = True
                    else:
                        self.useProxies = False
    
                    if "https" in u_var:
                        print(u_var)
                        self.use_url = True
                        self.url = u_var
                    else:
                        self.use_url = False
                        self.variant = u_var
                    t = threading.Thread(target= self.ReadProfile).start()
                else:
                    pass

    def ReadProfile(self):
        self.lock.acquire()
        try:
            with open(f'../PROFILES/profile_{self.profilename}.json','r') as task_prof:
                self.profile = json.load(task_prof)
        finally:
            print(f'| {get_t_name()} | PROFILE LOADED')
            self.lock.release()

        if self.use_url == False:
            self.cart()
        else:
            self.scrape()
    
    def scrape(self):
        if '?variant' in self.url:
            self.url = self.url.split('?variant')[0]
        else:
            pass
        
        scrapeURL = f'{self.url}.json'

        r = requests.get(scrapeURL,headers=headers)
        jsonRESP = r.json()
        self.ProductTitle = jsonRESP["product"]["title"]
        productVariants = jsonRESP["product"]["variants"]
        for v in productVariants:
            if self.size == v["option2"]:
                self.variant = v["id"]
                self.productPrice = v["price"]
                size_found = True
            else:
                pass
        
        if size_found == True:
            print(f'| {get_t_name()} | SIZE FOUND ({self.size})')
            self.cart()
        else:
            print(f'| {get_t_name()} | SIZE NOT FOUND')
        


    def cart(self):
        if self.useProxies == True:
            self.proxies = loadProxy()
            print(f'| {get_t_name()} | PROXY LOADED')
        else:
            self.proxies = None

        self.sess = requests.session()
        self.sess.headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }

        print(f'| {get_t_name()} | ADDING TO CART')
        try:
            cart = self.sess.get(f'{self.base}/cart/add.js?quantity=1&id={self.variant}',proxies=self.proxies)
        except requests.exceptions.ConnectionError:
            print("error")
        if cart.status_code != 200:
            print(f'| {get_t_name()} | ERROR CARTING. RETRYING...')
            time.sleep(int(self.delay))
            self.cart()
        elif cart.status_code == 200:
            print(f'| {get_t_name()} | CARTED PRODUCT')
            self.hook.send(f"{get_t_name()} | Carted!")
            self.PRODUCTdata = cart.json()

            self.PaymentTokenGrab()

    def PaymentTokenGrab(self):

        payment_load = {
            "credit_card": {
            "number": self.profile["CARD-NUMBER"],
            "name": f'{self.profile["FIRST-NAME"]} {self.profile["LAST-NAME"]}',
            "month": self.profile["CARD-EXP-M"],
            "year": self.profile["CARD-EXP-Y"],
            "verification_value": self.profile["CARD-CVV"]
        }
        }

        try:
            grab = self.sess.post('https://elb.deposit.shopifycs.com/sessions',json=payment_load,proxies=self.proxies)
        except requests.exceptions.ConnectionError:
            print(f'| {get_t_name()} | CONNECTION ERROR. SLEEPING...')
            time.sleep(int(self.delay))
            self.PaymentTokenGrab()

        self.paymentToken = grab.json()["id"]
        if self.paymentToken == None:
            print(f'| {get_t_name()} | FAILED FETCHING PAYMENT TOKEN. RETRYING...')
            self.PaymentTokenGrab()
        else:
            print(f'| {get_t_name()} | FETCHED PAYMENT TOKEN')
            self.hook.send(f"{get_t_name()} | token fetched!")
            self.Checkout()

    def Checkout(self):
        try:
            get_checkout = self.sess.get(f'{self.base}/checkout',proxies=self.proxies)
        except requests.exceptions.ConnectionError:
            print(f'| {get_t_name()} | CONNECTION ERROR. SLEEPING...')
            time.sleep(int(self.delay))
            self.Checkout()
        if get_checkout.status_code == 200:
            if "throttle/queue?" in get_checkout.url:
                print(f'| {get_t_name()} | POLLING QUEUE...')
                while "throttle/queue?" in get_checkout.url:
                    try:
                        poll = self.sess.get(f'{self.base}/checkout/poll?js_poll=1',proxies=self.proxies)
                    except requests.exceptions.ConnectionError:
                        print(f'| {get_t_name()} | CONNECTION ERROR. SLEEPING...')
                        time.sleep(int(self.delay))
                        self.Checkout()
                    if poll.status_code == 200:
                        print(f'| {get_t_name()} | PASSED QUEUE !')
                        try:
                            get_checkout = self.sess.get(f'{self.base}/checkout',proxies=self.proxies)
                        except requests.exceptions.ConnectionError:
                            print(f'| {get_t_name()} | CONNECTION ERROR. SLEEPING...')
                            time.sleep(int(self.delay))
                            self.Checkout()
                        self.checkouturl = get_checkout.url
                        self.check()
            else:
                print(f'| {get_t_name()} | NO QUEUE')
                self.checkouturl = get_checkout.url
                self.check()
        else:
            print(f'| {get_t_name()} | ERROR REQUESTING CHECKOUT')
            self.Checkout()
    
    def check(self):
        try:
            get_page = self.sess.get(self.checkouturl,proxies=self.proxies)
        except requests.exceptions.ConnectionError:
            print(f'| {get_t_name()} | CONNECTION ERROR. SLEEPING...')
            time.sleep(int(self.delay))
            self.check()
        if "stock_problems" in self.checkouturl:
            print(f'| {get_t_name()} | PRODUCT OOS. RETYING...')
            while "stock_problems" in self.checkouturl:
                print(f'| {get_t_name()} | PRODUCT OOS. RETYING...')
                try:
                    get_page = self.sess.get(self.checkouturl,proxies=self.proxies)
                except requests.exceptions.ConnectionError:
                    print(f'| {get_t_name()} | CONNECTION ERROR. SLEEPING...')
                    time.sleep(int(self.delay))
                    self.check()
                if "stock_problems" not in get_page.url:
                    print(f'| {get_t_name()} | PROCEEDING TO CHECKOUT')
                    self.hook.send(f"{get_t_name()} | proceeding to checkout!")
                    self.address()
        elif "stock_problems" not in self.checkouturl:
            print(f'| {get_t_name()} | PROCEEDING TO CHECKOUT')
            self.hook.send(f"{get_t_name()} | proceeding to checkout!")
            self.address()

    def address(self):
        payload = {
            '_method': 'patch',
            'authenticity_token': '',
            'previous_step': 'contact_information',
            'step': 'shipping_method',
            'checkout[email]': self.profile["EMAIL"],
            'checkout[buyer_accepts_marketing]': 0,
            'checkout[shipping_address][first_name]': self.profile["FIRST-NAME"],
            'checkout[shipping_address][last_name]': self.profile["LAST-NAME"],
            'checkout[shipping_address][company]': '',
            'checkout[shipping_address][address1]': self.profile["ADDRESS-1"],
            'checkout[shipping_address][address2]': self.profile["ADDRESS-2"],
            'checkout[shipping_address][city]': self.profile["CITY"],
            'checkout[shipping_address][country]': self.profile["COUNTRY"],
            'checkout[shipping_address][province]': self.profile["PROVINCE"],
            'checkout[shipping_address][zip]': self.profile["POST-CODE"],
            'checkout[shipping_address][phone]': self.profile["PHONE"],
            'checkout[shipping_address][first_name]': self.profile["FIRST-NAME"],
            'checkout[shipping_address][last_name]': self.profile["LAST-NAME"],
            'checkout[shipping_address][company]': '',
            'checkout[shipping_address][address1]': self.profile["ADDRESS-1"],
            'checkout[shipping_address][address2]': self.profile["ADDRESS-2"],
            'checkout[shipping_address][city]': self.profile["CITY"],
            'checkout[shipping_address][country]': self.profile["COUNTRY"],
            'checkout[shipping_address][zip]': self.profile["POST-CODE"],
            'checkout[shipping_address][phone]': self.profile["PHONE"],
            'checkout[client_details][browser_width]': 1280,
            'checkout[client_details][browser_height]': 1281,
            'checkout[client_details][javascript_enabled]': 1,
            'checkout[client_details][color_depth]': 24,
            'checkout[client_details][java_enabled]': False,
            'checkout[client_details][browser_tz]': 0,
        }

        try:
            SENDpayload = self.sess.post(self.checkouturl,data=payload,proxies=self.proxies)
        except requests.exceptions.ConnectionError:
            print(f'| {get_t_name()} | CONNECTION ERROR. SLEEPING...')
            time.sleep(int(self.delay))
            self.address()
        if SENDpayload.status_code == 200:
            self.checkouturl = SENDpayload.url
            print(f'| {get_t_name()} | SUBMITTED ADDRESS')
            self.hook.send(f"{get_t_name()} | submitted addy!")
            self.shipping()
        else:
            print(f'| {get_t_name()} | ENCOUNTERED ERROR. RETRYING... [{SENDpayload.status_code}]')
            self.address()

    def shipping(self):
        try:
            get_page = self.sess.get(self.checkouturl,proxies=self.proxies)
        except requests.exceptions.ConnectionError:
            print(f'| {get_t_name()} | CONNECTION ERROR. SLEEPING...')
            time.sleep(int(self.delay))
            self.shipping()
        self.checkouturl = get_page.url

        soup = BeautifulSoup(get_page.text,"html.parser")
        try:
            self.shippingRate = soup.find("div",{"class":"radio-wrapper"})["data-shipping-method"]
            print(f'| {get_t_name()} | FETCHED SHIPPING RATES')
            self.hook.send(f"{get_t_name()} | shipping rates fetched!")
        except:
            print(f'| {get_t_name()} | FAILED TO FETCH SHIPPING RATES. RETRYING...')
            self.shipping()


        
        payload = {
            '_method': 'patch',
            'authenticity_token':'',
            'previous_step': 'shipping_method',
            'step': 'payment_method',
            'checkout[shipping_rate][id]': self.shippingRate,
            'checkout[client_details][browser_width]': 1279,
            'checkout[client_details][browser_height]': 1288,
            'checkout[client_details][javascript_enabled]': 1,
            'checkout[client_details][color_depth]': 24,
            'checkout[client_details][java_enabled]': False,
            'checkout[client_details][browser_tz]': 0,
        }
        try:
            SENDpayload = self.sess.post(self.checkouturl,data=payload,proxies=self.proxies)
        except requests.exceptions.ConnectionError:
            print(f'| {get_t_name()} | CONNECTION ERROR. SLEEPING...')
            time.sleep(int(self.delay))
            self.shipping()
        self.checkouturl = SENDpayload.url
        if SENDpayload.status_code == 200:
            print(f'| {get_t_name()} | SHIPPING SUBMITTED')
            self.hook.send(f"{get_t_name()} | shipping submitted!")
            self.payment()
        else:
            self.shipping()

    def payment(self):
        self.checkouturl = self.checkouturl.replace("?locale=en&previous_step=contact_information&step=shipping_method","?from_processing_page=1&validate=true")
        print(f'| {get_t_name()} | SUBMITTING ORDER')
        self.hook.send(f"{get_t_name()} | submitting order!")
        try:
            GETpaymentPage = self.sess.get(self.checkouturl,proxies=self.proxies)
        except requests.exceptions.ConnectionError:
            print(f'| {get_t_name()} | CONNECTION ERROR. SLEEPING...')
            time.sleep(int(self.delay))
            self.payment()

      
        soup = BeautifulSoup(GETpaymentPage.text,"html.parser")
        try:
            self.gateway = soup.find("input",{"class":"input-radio"})["value"]
        except:
            self.payment()
        payload = {
            '_method': 'patch',
            'authenticity_token': '',
            'previous_step': 'payment_method',
            'step': '',
            's': self.paymentToken,
            'checkout[payment_gateway]': self.gateway,
            'checkout[credit_card][vault]': False,
            'checkout[different_billing_address]': False,
            'checkout[remember_me]': False,
            'checkout[remember_me]': 0,
            'checkout[vault_phone]': '',
            'checkout[total_price]': 21500,
            'complete': 1,
            'checkout[client_details][browser_width]': 1279,
            'checkout[client_details][browser_height]': 1288,
            'checkout[client_details][javascript_enabled]': 1,
            'checkout[client_details][color_depth]': 24,
            'checkout[client_details][java_enabled]': False,
            'checkout[client_details][browser_tz]': 0,
        }
        print(f'| {get_t_name()} | PROCESSING...')
        self.hook.send(f"{get_t_name()} | processing!")
        try:
            SENDpayload = self.sess.post(self.checkouturl,data=payload,proxies=self.proxies)
        except requests.exceptions.ConnectionError:
            print(f'| {get_t_name()} | CONNECTION ERROR. SLEEPING...')
            time.sleep(int(self.delay))
            self.payment()
        if "thank" in SENDpayload.url:
            print(f'| {get_t_name()} | CHECKOUT SUCCESS')
            self.hook.send(f"{get_t_name()} | checkout success!")
        else:
            print(f'| {get_t_name()} | ERROR CHECKING OUT')
            self.hook.send(f"{get_t_name()} | checkout error!")
            print(SENDpayload)
            print(SENDpayload.url)



if __name__ == "__main__":
    Main()
