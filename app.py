from flask import Flask, render_template, request
import requests

app = Flask(__name__)
API_KEY = "5baa53d864f947eb833105947251308"

last_searches = []

def get_weather(city):
    try:
        url = f"https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&aqi=no"
        res = requests.get(url)
        data = res.json()
        if "error" in data:
            return {"error": data["error"]["message"]}
        weather = {
            "city": data["location"]["name"],
            "country": data["location"]["country"],
            "temp": data["current"]["temp_c"],
            "humidity": data["current"]["humidity"],
            "wind_speed": data["current"]["wind_kph"],
            "description": data["current"]["condition"]["text"],
            "icon": "https:" + data["current"]["condition"]["icon"]
        }
        last_searches.insert(0, weather)
        if len(last_searches) > 5:
            last_searches.pop()
        return weather
    except Exception as e:
        return {"error": str(e)}

@app.route('/', methods=['GET', 'POST'])
def home():
    weather = None
    error = None
    if request.method == 'POST':
        city = request.form.get('city')
        result = get_weather(city)
        if "error" in result:
            error = result["error"]
        else:
            weather = result
    return render_template('weather.html', weather=weather, error=error)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/history')
def history():
    return render_template('history.html', searches=last_searches)

if __name__ == '__main__':
    app.run()
