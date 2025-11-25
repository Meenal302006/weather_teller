from flask import Flask, render_template, request
import requests
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Create database table
def init_db():
    conn = sqlite3.connect("weather.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            temperature REAL,
            humidity INTEGER,
            condition TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Log weather data
def log_weather(city, temp, humidity, condition):
    conn = sqlite3.connect("weather.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO logs (city, temperature, humidity, condition, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (city, temp, humidity, condition, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def home():
    weather_data = None
    error = None

    if request.method == "POST":
        city = request.form["city"]
        api_key = "477f2c0f623d37c2fb05fe02a227cf9d"  # Add your OpenWeatherMap API key

        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url)

            if response.status_code != 200:
                raise Exception("Invalid city name")

            data = response.json()

            weather_data = {
                "city": city,
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "condition": data["weather"][0]["description"]
            }

            # Log in database
            log_weather(
                weather_data["city"],
                weather_data["temperature"],
                weather_data["humidity"],
                weather_data["condition"]
            )

        except Exception as e:
            error = str(e)

    return render_template("index.html", weather=weather_data, error=error)

if __name__ == "__main__":
    app.run(debug=True)
