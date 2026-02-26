import requests

api_url_4_location = "https://nc6apta5vj.re.qweatherapi.com/geo/v2/city/lookup?location="
headers = {"X-QW-Api-Key": "0215c76d1f264eb0bcc1f153bb04f204","User-Agent":"Mozilla/5.0"}
api_url_4_weather = "https://nc6apta5vj.re.qweatherapi.com/v7/weather/now?location="


city = input("请输入你的城市")
api_url_4_location = api_url_4_location + city
r = requests.get(api_url_4_location,headers=headers)
data = r.json()
print(data)
city_id = data['location'][0]['id']
#
api_url_4_weather = api_url_4_weather + str(city_id)
#
r = requests.get(api_url_4_weather,headers=headers)
#
data = r.json()
print(data)
temp = data['now']['temp']
temp = int(temp)
feels_like = data['now']['feelsLike']
weather = data['now']['text']
print(f"{city}天气：{weather}")
print(f"今日温度：{temp}")
print(f"今日体感温度：{feels_like}")

if temp <5:
    print("天气较冷，适合穿羽绒服")
elif temp <20:
    print("天气温和，适合穿卫衣")
