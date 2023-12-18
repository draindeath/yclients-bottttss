import httpx
import ujson
import pprint

class YClients:
    def __init__(self, shop_id:int = None, company_id:int = None) -> None:
        self.auth_headers = {
            "authorization": "Bearer gtcwf654agufy25gsadh"
        }
        self.shop_id = shop_id
        self.company_id = company_id
        self.time = ""
        self.datetime = ""
        self.staff_id = ""
        self.service_ids = []
        self.base_url = f"https://n{shop_id}.yclients.com"
        self.url_api = f"{self.base_url}/api/v1/"

        self.month_strings = {
            1: "января",
            2: "февраля",
            3: "марта",
            4: "апреля",
            5: "мая",
            6: "июня",
            7: "июля",
            8: "августа",
            9: "сентября",
            10: "октября",
            11: "ноября",
            12: "декабря"
        }

    def date_to_string(self, date:str) -> str:
        year, month, day = date.split("-")
        return f"{day} {self.month_strings[int(month)]}"

    def get_categories_and_services(self) -> list:
        """Получить список категорий и сервисов"""
        url = self.url_api + f"book_services/{self.company_id}?staff_id={self.staff_id}&datetime={self.time if self.time else self.datetime}"
        response = httpx.get(url, headers = self.auth_headers).json()
        categories = self.__prepare_categories(response['category'])
        self.__prepare_services(response['services'], categories)
        return categories

    def get_raw_services(self) -> list:
        """Получить список сервисов"""
        url = self.url_api + f"book_services/{self.company_id}?"
        response = httpx.get(url, headers = self.auth_headers).json()
        return response['services']

    def get_staff(self) -> list:
        """Получить список специалистов"""
        url = self.url_api + f"book_staff/{self.company_id}?datetime={self.time if self.time else self.datetime}&without_seances=1{self.__convert_service_ids_to_string(self.service_ids)}"
        response = httpx.get(url, headers = self.auth_headers)
        return response.json()
    
    def get_dates(self) -> dict:
        """Получить список дат для бронирования"""
        url = self.url_api + f"book_dates/{self.company_id}?staff_id={self.staff_id}{self.__convert_service_ids_to_string(self.service_ids)}"
        response = httpx.get(url, headers = self.auth_headers)
        dates = {date:self.date_to_string(date) for date in response.json()['booking_dates']}
        return dates
    
    def get_times(self) -> list:
        """Получить список времени для бронирования"""
        url = self.url_api + f"book_times/{self.company_id}/{self.staff_id if self.staff_id else 0}/{self.datetime}?{self.__convert_service_ids_to_string(self.service_ids)}"
        response = httpx.get(url, headers = self.auth_headers)
        return response.json()

    def set_staff_id(self, staff_id:int) -> None:
        """Выбор специалиста, указывать пустые кавычки если пользователь нажал отмену выбора"""
        self.staff_id = staff_id
        return True
    
    def set_datetime(self, datetime:str) -> None:
        self.datetime = datetime if datetime else ""
        return True
    
    def set_time(self, datetime:str) -> None:
        self.time = datetime.replace("+0300", "") if datetime else ""
        return True
    
    def add_service_id(self, service_id:int) -> None:
        self.service_ids.append(service_id)

    def reset_service_ids(self) -> None:
        self.service_ids = []

    def remove_service_id(self, service_id:int) -> None:
        self.service_ids.remove(service_id)

    def send_record(self, fullname: str, phone_number: str, email: str = "", comment:str = "") -> None:
        data = {
            "fullname": fullname,
            "phone": phone_number,
            "email": email,
            "comment": comment,
            "appointments": [
                {
                    "services": self.service_ids,
                    "staff_id": self.staff_id,
                    "datetime": self.time,
                    "chargeStatus":"","id":0
                }
            ],
            "bookform_id": self.shop_id,
            "isMobile": False,
            "notify_by_sms":24,
            "referrer":"",
            "is_charge_required_priority": True,
            "is_support_charge": False,
            "appointments_charges":[
                {
                    "id":0,
                    "services":[],
                    "prepaid":[]
                }
            ],
            "redirect_url": f"https://n{self.shop_id}.yclients.com/company/{self.company_id}/success-order/"+"{recordId}/{recordHash}"
        }

        url = self.url_api + f"book_record/{self.company_id}"

        resp = httpx.post(url, headers = self.auth_headers, json = data)
        return resp.json()
    
    def __prepare_categories(self, categories:list) -> dict:
        data = {}
        for category in categories:
            data[category['id']] = {"title": category['title'], "services": []}
        return data

    def __prepare_services(self, services:list, categories:dict) -> list:
        for service in services:
            categories[service['category_id']]['services'].append({"title": service['title'], "price": service['price_max'], "seance_length": service['seance_length'], "id": service['id']})

    def __convert_service_ids_to_string(self, service_ids:list) -> str:
        if service_ids:
            return "&" + "&".join([f"service_ids[]={service_id}" for service_id in service_ids])
        else: return ''