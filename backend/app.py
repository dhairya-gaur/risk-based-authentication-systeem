from flask import Flask, request, render_template
import requests

app = Flask(__name__)


def get_client_ip():
    """
    Get the real client IP address.
    If behind a proxy/load balancer (e.g. Nginx, Heroku, Render), the real IP
    is usually in the X-Forwarded-For header, not request.remote_addr.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can be a comma-separated list; the first is the original client
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr


def lookup_location(ip_address):
    """
    Query ipapi.co for geolocation data on a given IP.
    Returns a dict with location info, or an error message.
    """
    # Skip lookup for localhost — it won't resolve to a real location
    if ip_address in ("127.0.0.1", "::1", "localhost"):
        return {"error": "Running locally — no public IP to look up."}

    try:
        response = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("error"):
            return {"error": data.get("reason", "Lookup failed")}

        return {
            "ip": data.get("ip"),
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country_name"),
            "postal": data.get("postal"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("timezone"),
            "isp": data.get("org"),
        }
    except requests.RequestException as e:
        return {"error": f"Could not reach geolocation service: {e}"}


@app.route("/")
def index():
    client_ip = get_client_ip()
    location = lookup_location(client_ip)
    return render_template("index.html", ip=client_ip, location=location)


@app.route("/api/location")
def api_location():
    """JSON endpoint — useful if you want to call this from JS or another service."""
    client_ip = get_client_ip()
    location = lookup_location(client_ip)
    return {"ip": client_ip, "location": location}


if __name__ == "__main__":
    app.run(debug=True, port=5000)