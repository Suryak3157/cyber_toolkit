import dns.resolver

def run_dns(domain):
    result = {}

    try:
        # ✅ A Records (IP)
        try:
            a_records = dns.resolver.resolve(domain, 'A')
            result["A Records"] = [str(r) for r in a_records]
        except:
            result["A Records"] = ["Not found"]

        # ✅ NS Records
        try:
            ns_records = dns.resolver.resolve(domain, 'NS')
            result["Name Servers"] = [str(r) for r in ns_records]
        except:
            result["Name Servers"] = ["Not found"]

        # ✅ MX Records
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            result["Mail Servers"] = [str(r.exchange) for r in mx_records]
        except:
            result["Mail Servers"] = ["Not found"]

        # ✅ TXT Records
        try:
            txt_records = dns.resolver.resolve(domain, 'TXT')
            result["TXT Records"] = [str(r) for r in txt_records]
        except:
            result["TXT Records"] = ["Not found"]

        return result

    except Exception as e:
        return {"Error": str(e)}