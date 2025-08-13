from flask import Flask, render_template, request, flash, redirect, url_for, make_response
import requests
import json
from pycountry import countries
from datetime import datetime

app = Flask(__name__)
app.secret_key = "quick-key-123" 
API_KEY = "5baa53d864f947eb833105947251308"

def get_weather(city, country):
    try:
        url = f"https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city},{country}&aqi=no"
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
            "icon": "https:" + data["current"]["condition"]["icon"],
            "timestamp": datetime.now().strftime("%b %d, %Y, %I:%M %p")
        }
        return weather
    except Exception as e:
        return {"error": str(e)}

@app.route("/", methods=["GET", "POST"])
def home():
    weather = None
    history = request.cookies.get("weather_history")
    searches = json.loads(history) if history else []

    if request.method == "POST":
        city = request.form.get("city")
        country = request.form.get("country")
        is_update = "city" in request.form and "country" in request.form and searches and searches[0]["city"] == city
        if not is_update and not countries.get(alpha_2=country.upper()):
            flash("No matching location found in weather API", "danger")
            return redirect(url_for("home"))
        result = get_weather(city, country)
        if "error" in result:
            flash(result["error"], "danger")
            return redirect(url_for("home"))
        else:
            searches.insert(0, result)
            response = make_response(redirect(url_for("home", city=city, country=country)))
            response.set_cookie("weather_history", json.dumps(searches), max_age=30*24*60*60)  
            return response
    else:
        city = request.args.get("city")
        country = request.args.get("country")
        if city and country:
            result = get_weather(city, country)
            if "error" in result:
                flash(result["error"], "danger")
            else:
                weather = result
        return render_template("weather.html", weather=weather, searches=searches)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/history")
def history():
    history = request.cookies.get("weather_history")
    searches = json.loads(history) if history else []
    return render_template("history.html", searches=searches)

if __name__ == "__main__":
    app.run(debug=True)