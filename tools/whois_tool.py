import whois
import socket

def format_date(value):
    if isinstance(value, list):
        return value[0]
    return value

def get_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except:
        return "Not found"

def run_whois(domain):
    try:
        if not domain or "." not in domain:
            return {"Error": "Invalid domain"}

        data = whois.whois(domain)

        result = {
            "Domain Name": data.domain_name,
            "Registrar": data.registrar,
            "Creation Date": str(format_date(data.creation_date)),
            "Expiration Date": str(format_date(data.expiration_date)),
            "Updated Date": str(format_date(data.updated_date)),
            "Name Servers": ", ".join(data.name_servers) if data.name_servers else "N/A",
            "IP Address": get_ip(domain)
        }

        return result

    except Exception as e:
        return {"Error": str(e)}