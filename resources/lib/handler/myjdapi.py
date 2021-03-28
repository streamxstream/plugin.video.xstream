# -*- encoding: utf-8 -*-
from resources.lib import pyaes
import hashlib, hmac, json, time, base64
import requests
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote


class MYJDException(BaseException):
    pass


def PAD(s):
    BS = 16
    try:
        return s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode()
    except Exception:
        return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)


def UNPAD(s):
    try:
        return s[0:-s[-1]]
    except Exception:
        return s[0:-ord(s[-1])]


class System:
    def __init__(self, device):
        self.device = device
        self.url = '/system'

    def exit_jd(self):
        return self.device.action(self.url + "/exitJD")

    def restart_jd(self):
        return self.device.action(self.url + "/restartJD")

    def hibernate_os(self):
        return self.device.action(self.url + "/hibernateOS")

    def shutdown_os(self, force):
        return self.device.action(self.url + "/shutdownOS", force)

    def standby_os(self):
        return self.device.action(self.url + "/standbyOS")


class Update:
    def __init__(self, device):
        self.device = device
        self.url = '/update'

    def restart_and_update(self):
        return self.device.action(self.url + "/restartAndUpdate")

    def run_update_check(self):
        return self.device.action(self.url + "/runUpdateCheck")

    def is_update_available(self):
        return self.device.action(self.url + "/isUpdateAvailable")


class DownloadController:
    def __init__(self, device):
        self.device = device
        self.url = '/downloadcontroller'

    def start_downloads(self):
        return self.device.action(self.url + "/start")

    def stop_downloads(self):
        return self.device.action(self.url + "/stop")

    def pause_downloads(self, value):
        params = [value]
        return self.device.action(self.url + "/pause", params)

    def get_speed_in_bytes(self):
        return self.device.action(self.url + "/getSpeedInBps")

    def force_download(self, link_ids, package_ids):
        params = [link_ids, package_ids]
        return self.device.action(self.url + "/forceDownload", params)

    def get_current_state(self):
        return self.device.action(self.url + "/getCurrentState")


class Linkgrabber:

    def __init__(self, device):
        self.device = device
        self.url = '/linkgrabberv2'

    def clear_list(self):
        return self.device.action(self.url + "/clearList", http_action="POST")

    def move_to_downloadlist(self, links_ids, packages_ids):
        params = [links_ids, packages_ids]
        return self.device.action(self.url + "/moveToDownloadlist", params)

    def query_links(self, params=[
        {"bytesTotal": True,
         "comment": True,
         "status": True,
         "enabled": True,
         "maxResults": -1,
         "startAt": 0,
         "hosts": True,
         "url": True,
         "availability": True,
         "variantIcon": True,
         "variantName": True,
         "variantID": True,
         "variants": True,
         "priority": True}]):
        return self.device.action(self.url + "/queryLinks", params)

    def cleanup(self, action, mode, selection_type, links_ids=[], packages_ids=[]):
        params = [links_ids, packages_ids]
        params += [action, mode, selection_type]
        return self.device.action(self.url + "/cleanup", params)

    def add_container(self, type_, content):
        params = [type_, content]
        return self.device.action(self.url + "/addContainer", params)

    def get_download_urls(self, links_ids, packages_ids, url_display_type):
        params = [packages_ids, links_ids, url_display_type]
        return self.device.action(self.url + "/getDownloadUrls", params)

    def set_priority(self, priority, links_ids, packages_ids):
        params = [priority, links_ids, packages_ids]
        return self.device.action(self.url + "/setPriority", params)

    def set_enabled(self, params):
        return self.device.action(self.url + "/setEnabled", params)

    def get_variants(self, params):
        return self.device.action(self.url + "/getVariants", params)

    def add_links(self, params=[
        {"autostart": False,
         "links": None,
         "packageName": None,
         "extractPassword": None,
         "priority": "DEFAULT",
         "downloadPassword": None,
         "destinationFolder": None,
         "overwritePackagizerRules": False}]):
        return self.device.action("/linkgrabberv2/addLinks", params)

    def get_childrenchanged(self):
        pass

    def remove_links(self):
        pass

    def get_downfolderhistoryselectbase(self):
        pass

    def help(self):
        return self.device.action("/linkgrabberv2/help", http_action="GET")

    def rename_link(self):
        pass

    def move_links(self):
        pass

    def set_variant(self):
        pass

    def get_package_count(self):
        pass

    def rename_package(self):
        pass

    def query_packages(self):
        pass

    def move_packages(self):
        pass

    def add_variant_copy(self):
        pass


class Downloads:
    def __init__(self, device):
        self.device = device
        self.url = "/downloadsV2"

    def query_links(self, params=[
        {"bytesTotal": True,
         "comment": True,
         "status": True,
         "enabled": True,
         "maxResults": -1,
         "startAt": 0,
         "packageUUIDs": [],
         "host": True,
         "url": True,
         "bytesloaded": True,
         "speed": True,
         "eta": True,
         "finished": True,
         "priority": True,
         "running": True,
         "skipped": True,
         "extractionStatus": True}]):
        return self.device.action(self.url + "/queryLinks", params)

    def query_packages(self, params=[
        {"bytesLoaded": True,
         "bytesTotal": True,
         "comment": True,
         "enabled": True,
         "eta": True,
         "priority": True,
         "finished": True,
         "running": True,
         "speed": True,
         "status": True,
         "childCount": True,
         "hosts": True,
         "saveTo": True,
         "maxResults": -1,
         "startAt": 0}]):
        return self.device.action(self.url + "/queryPackages", params)

    def cleanup(self, action, mode, selection_type, links_ids=[], packages_ids=[]):
        params = [links_ids, packages_ids]
        params += [action, mode, selection_type]
        return self.device.action(self.url + "/cleanup", params)


class Jddevice:

    def __init__(self, jd, device_dict):
        self.name = device_dict["name"]
        self.device_id = device_dict["id"]
        self.device_type = device_dict["type"]
        self.myjd = jd
        self.linkgrabber = Linkgrabber(self)
        self.downloads = Downloads(self)
        self.downloadcontroller = DownloadController(self)
        self.update = Update(self)
        self.system = System(self)

    def action(self, path, params=(), http_action="POST"):
        action_url = self.__action_url()
        response = self.myjd.request_api(path, http_action, params, action_url)
        if response is None:
            return False
        return response['data']

    def __action_url(self):
        return "/t_" + self.myjd.get_session_token() + "_" + self.device_id


class Myjdapi:

    def __init__(self):
        self.__request_id = int(time.time() * 1000)
        self.__api_url = "http://api.jdownloader.org"
        self.__app_key = "http://git.io/vmcsk"
        self.__api_version = 1
        self.__devices = None
        self.__login_secret = None
        self.__device_secret = None
        self.__session_token = None
        self.__regain_token = None
        self.__server_encryption_token = None
        self.__device_encryption_token = None
        self.__connected = False

    def get_session_token(self):
        return self.__session_token

    def is_connected(self):
        return self.__connected

    def set_app_key(self, app_key):
        self.__app_key = app_key

    def __secret_create(self, email, password, domain):
        secret_hash = hashlib.sha256()
        secret_hash.update(email.lower().encode('utf-8') + password.encode('utf-8') + domain.lower().encode('utf-8'))
        return secret_hash.digest()

    def __update_encryption_tokens(self):
        if self.__server_encryption_token is None:
            old_token = self.__login_secret
        else:
            old_token = self.__server_encryption_token
        new_token = hashlib.sha256()
        new_token.update(old_token + bytearray.fromhex(self.__session_token))
        self.__server_encryption_token = new_token.digest()
        new_token = hashlib.sha256()
        new_token.update(self.__device_secret + bytearray.fromhex(self.__session_token))
        self.__device_encryption_token = new_token.digest()

    def __signature_create(self, key, data):
        signature = hmac.new(key, data.encode('utf-8'), hashlib.sha256)
        return signature.hexdigest()

    def __decrypt(self, secret_token, data):
        init_vector = secret_token[:len(secret_token) // 2]
        key = secret_token[len(secret_token) // 2:]
        decryptor = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, init_vector))
        decrypted_data = decryptor.feed(base64.b64decode(data))
        decrypted_data += decryptor.feed()
        return decrypted_data

    def __encrypt(self, secret_token, data):
        data = PAD(data.encode('utf-8'))
        length = 16 - (len(data) % 16)
        data += chr(length).encode() * length
        init_vector = secret_token[:len(secret_token) // 2]
        key = secret_token[len(secret_token) // 2:]
        encryptor = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(key, init_vector))
        encrypted_data = encryptor.feed(data)
        encrypted_data += encryptor.feed()
        encrypted_data = base64.b64encode(encrypted_data)
        return encrypted_data.decode('utf-8')

    def update_request_id(self):
        self.__request_id = int(time.time())

    def connect(self, email, password):
        self.__login_secret = self.__secret_create(email, password, "server")
        self.__device_secret = self.__secret_create(email, password, "device")
        response = self.request_api("/my/connect", "GET", [("email", email), ("appkey", self.__app_key)])
        self.__connected = True
        self.update_request_id()
        self.__session_token = response["sessiontoken"]
        self.__regain_token = response["regaintoken"]
        self.__update_encryption_tokens()
        self.update_devices()

    def reconnect(self):
        response = self.request_api("/my/reconnect", "GET", [("sessiontoken", self.__session_token), ("regaintoken", self.__regain_token)])
        self.update_request_id()
        self.__session_token = response["sessiontoken"]
        self.__regain_token = response["regaintoken"]
        self.__update_encryption_tokens()

    def disconnect(self):
        self.request_api("/my/disconnect", "GET", [("sessiontoken", self.__session_token)])
        self.update_request_id()
        self.__login_secret = None
        self.__device_secret = None
        self.__session_token = None
        self.__regain_token = None
        self.__server_encryption_token = None
        self.__device_encryption_token = None
        self.__devices = None
        self.__connected = False

    def update_devices(self):
        response = self.request_api("/my/listdevices", "GET", [("sessiontoken", self.__session_token)])
        self.update_request_id()
        self.__devices = response["list"]

    def list_devices(self):
        return self.__devices

    def get_device(self, device_name=None, device_id=None):
        if not self.is_connected():
            raise (MYJDException("No connection established\n"))
        if device_id is not None:
            for device in self.__devices:
                if device["id"] == device_id:
                    return Jddevice(self, device)
        elif device_name is not None:
            for device in self.__devices:
                if device["name"] == device_name:
                    return Jddevice(self, device)
        raise MYJDException("Device not found\n")

    def request_api(self, path, http_method="GET", params=None, action=None):
        data = None
        if not self.is_connected() and path != "/my/connect":
            raise (MYJDException("No connection established\n"))
        if http_method == "GET":
            query = [path + "?"]
            for param in params:
                if param[0] != "encryptedLoginSecret":
                    query += ["%s=%s" % (param[0], quote(param[1]))]
                else:
                    query += ["&%s=%s" % (param[0], param[1])]
            query += ["rid=" + str(self.__request_id)]
            if self.__server_encryption_token is None:
                query += ["signature=" + str(self.__signature_create(self.__login_secret, query[0] + "&".join(query[1:])))]
            else:
                query += ["signature=" + str(self.__signature_create(self.__server_encryption_token, query[0] + "&".join(query[1:])))]
            query = query[0] + "&".join(query[1:])
            encrypted_response = requests.get(self.__api_url + query)
        else:
            params_request = []
            for param in params:
                if not isinstance(param, list):
                    params_request += [json.dumps(param)]
                else:
                    params_request += [param]
            params_request = {"apiVer": self.__api_version, "url": path, "params": params_request, "rid": self.__request_id}
            data = json.dumps(params_request).replace('"null"', "null").replace("'null'", "null")
            encrypted_data = self.__encrypt(self.__device_encryption_token, data)
            if action is not None:
                request_url = self.__api_url + action + path
            else:
                request_url = self.__api_url + path
            encrypted_response = requests.post(request_url, headers={"Content-Type": "application/aesjson-jd; charset=utf-8"}, data=encrypted_data)
        if encrypted_response.status_code != 200:
            error_msg = json.loads(encrypted_response.text)
            msg = "\n\tSOURCE: " + error_msg["src"] + "\n\tTYPE: " + \
                  error_msg["type"] + "\n------\nREQUEST_URL: " + \
                  self.__api_url + path
            if http_method == "GET":
                msg += query
            msg += "\n"
            if data is not None:
                msg += "DATA:\n" + data
            raise (MYJDException(msg))
        if action is None:
            if not self.__server_encryption_token:
                response = self.__decrypt(self.__login_secret, encrypted_response.text)
            else:
                response = self.__decrypt(self.__server_encryption_token, encrypted_response.text)
        else:
            if params is not None:
                response = self.__decrypt(self.__device_encryption_token, encrypted_response.text)
            else:
                return {"data": response}
        jsondata = json.loads(response.decode('utf-8'))
        if jsondata['rid'] != self.__request_id:
            self.update_request_id()
            return None
        self.update_request_id()
        return jsondata
