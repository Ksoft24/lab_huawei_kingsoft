import requests

BASE_URL = "http://20.83.43.2:5000"

print("🔍 Health check")
print(requests.get(f"{BASE_URL}/api/health").json())

print("\n📊 Última lectura")
latest = requests.get(f"{BASE_URL}/api/readings/latest").json()
print(latest)

print("\n📈 Últimas 5 lecturas")
rows = requests.get(f"{BASE_URL}/api/readings?limit=5").json()
for r in rows:
    print(r)

print("\n📟 Lecturas por dispositivo (opta01)")
rows = requests.get(f"{BASE_URL}/api/readings/device/opta01").json()
print("Total:", len(rows))
