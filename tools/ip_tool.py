import requests
import ipaddress

def is_private_ip(ip):
    try:
        return ipaddress.ip_address(ip).is_private
    except:
        return False

def track_ip(ip):
    try:
        if is_private_ip(ip):
            return {"Error": "Private IP detected (cannot be tracked externally)"}

        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url, timeout=5).json()

        if response.get("status") != "success":
            return {"Error": "Invalid IP address"}

        result = {
            "IP": response.get("query"),
            "Country": response.get("country"),
            "Region": response.get("regionName"),
            "City": response.get("city"),
            "ISP": response.get("isp"),
            "Organization": response.get("org"),
            "Latitude": response.get("lat"),
            "Longitude": response.get("lon"),
            "Timezone": response.get("timezone")
        }

        return result

    except Exception as e:
        return {"Error": str(e)}