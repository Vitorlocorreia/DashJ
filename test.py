import urllib.request, urllib.parse, urllib.error
import http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
data = urllib.parse.urlencode({'username': 'rcgoleiros', 'password': 'rcgoleiros2026'}).encode()

# Need to pass Content-Type header
req = urllib.request.Request('http://127.0.0.1:5000/login', data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
opener.open(req)

try:
    resp = opener.open('http://127.0.0.1:5000/dashboard')
    print("Dashboard OK")
except urllib.error.HTTPError as e:
    print("Dashboard 500:")
    print(e.read().decode()[:1000])

try:
    resp = opener.open('http://127.0.0.1:5000/editar-dashboard')
    print("Editar OK")
except urllib.error.HTTPError as e:
    print("Editar 500:")
    print(e.read().decode()[:1000])
