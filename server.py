from flask import Flask
from flask import request
import pickle
from datetime import datetime
from pytz import timezone
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="password",
  database="WellnessBuddy"
)

mycursor = mydb.cursor()

pst = timezone('US/Pacific')

app = Flask(__name__)

@app.route("/test")
def hello():
    date_time = datetime.now(pst).strftime("%Y-%m-%d %H:%M:%S")
    fahrenheit = request.args.get("fahrenheit")
    celcius = request.args.get("celcius")
    humidity = request.args.get("humidity")
    sound = request.args.get("sound")
    vl = request.args.get("vl")
    il = request.args.get("il")
    uv = request.args.get("uv")
    steps = request.args.get("steps")
    heartrate = request.args.get("heartrate")
    sql = "INSERT INTO sensor_data (Timestamp, Humidity, Fahrenheit, Celcius, Sound, Visible_Light, Infrared_Light, UV_Index, Steps, Heartrate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (date_time, humidity, fahrenheit, celcius, sound, vl, il, uv, steps, heartrate)
    mycursor.execute(sql, val)
    print(mycursor.rowcount, "record inserted.")
    mydb.commit()
    return "Query executed with values: " + str(val)

def getAverage(type):
    query = "SELECT AVG({0}) FROM sensor_data".format(type)
    mycursor.execute(query)
    avg = mycursor.fetchall()
    return avg
    
def returnData(type):
    query = "SELECT Timestamp, {0} FROM sensor_data".format(type)
    mycursor.execute(query)
    data = mycursor.fetchall()
    return data
    
def createTable(type):
    table = []
    if type == 'Fahrenheit':
        table.append(['Time', 'Fahrenheit'])
        data = list(returnData('Fahrenheit'))
        table.extend([[str(item[0]), item[1]] for item in data])
    elif type == 'Celcius':
        table.append(['Time', 'Celcius'])
        data = list(returnData('Celcius'))
        table.extend([[str(item[0]), item[1]]  for item in data])
    elif type == 'Humidity':
        table.append(['Time', 'Humidity'])
        data = list(returnData('Humidity'))
        table.extend([[str(item[0]), item[1]]  for item in data])
    elif type == 'Sound':
        table.append(['Time', 'Sound'])
        data = list(returnData('Sound'))
        table.extend([[str(item[0]), item[1]]  for item in data])
    elif type == 'Visible_Light':
        table.append(['Time', 'Visible Light'])
        data = list(returnData('Visible_Light'))
        table.extend([[str(item[0]), item[1]]  for item in data])
    elif type == 'Infrared_Light':
        table.append(['Time', 'Infrared Light'])
        data = list(returnData('Infrared_Light'))
        table.extend([[str(item[0]), item[1]] for item in data])
    elif type == 'UV_Index':
        table.append(['Time', 'UV'])
        data = list(returnData('UV_Index'))
        table.extend([[str(item[0]), item[1]]  for item in data])
    elif type == 'Steps':
        table.append(['Time', 'Steps'])
        data = list(returnData('Steps'))
        table.extend([[str(item[0]), item[1]]  for item in data])
    elif type == 'Heartrate':
        table.append(['Time', 'Heartrate'])
        data = list(returnData('Heartrate'))
        table.extend([[str(item[0]), item[1]]  for item in data])
    return table, getAverage(type)
    
def recommendValue(type, currentAvg):
    # Humidity: 30-50%, never exceed 60%
    # F: 68-72
    # C: 20-22
    # Steps: 10000
    # Restig heartrate: 60 - 100 lower is better though
    # 0-2 UV Low risk 3-5 moderate 6-7 high 8-10 very high
    # 500 lumen for daily work
    recommended = 0
    currentAvg = currentAvg[0][0]
    if type == 'Fahrenheit':
        target = 68
        recommended = (currentAvg + target)/2
        if 68 <= currentAvg <= 72:
            return "The temperature is in the recommended range!"
        elif currentAvg < 68:
            return "It is a bit cold, try turning on the heater to reach 68-72 fahrenheit."
        else:
            return "It is a bit hot, try cooling down the room to 68-72 fahrenheit."
        #return "Average: {0} Recommended: {1} Target: {2}".format(currentAvg, recommended, target)
    elif type == 'Celcius':
        target = 20
        recommended = (currentAvg + target)/2
        if 20 <= currentAvg <= 22:
            return "The temperature is in the recommended range!"
        elif currentAvg < 20:
            return "It is a bit cold, try turning on the heater to reach 20-22 celcius."
        else:
            return "It is a bit hot, try cooling down the room to 20-22 celcius."
        #return "Average: {0} Recommended: {1} Target: {2}".format(currentAvg, recommended, target)
    elif type == 'Humidity':
        target = 40
        recommended = (currentAvg + target)/2
        if 30 <= currentAvg <= 50:
            return "Humidity is in the recommended range!"
        elif currentAvg < 30:
            return "The air is a bit dry. Try using a humidifier!"
        else:
            return "It is too humid! Try dehumidifying!"
        #return "Average: {0} Recommended: {1} Target: {2}".format(currentAvg, recommended, target)
    elif type == 'Sound':
        target = 1500
        #recommended = (currentAvg + target)/2
        if currentAvg <= 1500:
            return "Sound levels are safe!"
        return "Sound levels are a bit high! Try lowering your volume!"
        #return "Average: {0} Recommended: {1} Target: {2}".format(currentAvg, target)
    elif type == 'VL':
        target = 500
        recommended = (currentAvg + target)/2
        if 450 <= currentAvg <= 550:
            return "Light conditions are good for working!"
        elif currentAvg < 450:
            return "Your light levels are low! If you are working, try increasing the brightness!"
        else:
            return "It is very bright! Lowering the light level may make working conditions more comfortable."
        #return "Average: {0} Recommended: {1} Target: {2}".format(currentAvg, recommended, target)
    elif type == 'IL':
        target = 0
        recommended = (currentAvg + target)/2
        return "Average: {0} Recommended: {1} Target: {2}".format(currentAvg, recommended, target)
    elif type == 'UV':
        target = 0
        recommended = (currentAvg + target)/2
        if currentAvg <= 2:
            return "UV levels are safe!"
        elif  3 <= currentAvg <= 5:
            return "UV levels have moderate risk on your skin! Try reducing the amount of sun exposure!"
        elif 6 <= currentAvg <= 7:
            return "UV levels have high risk! Try reducing the amount of sun exposure!"
        elif currentAvg >= 8:
            return "You are at very high risk of sun damage!"
        #return "Average: {0} Recommended: {1} Target: {2}".format(currentAvg, recommended, target)
    elif type == 'Steps':
        target = 10000
        recommended = (currentAvg + target)/2
        if currentAvg >= 10000:
            return "You are walking a great amount!"
        return "Your steps a day are a bit low. Average: {0} Recommended: {1} Target: {2}".format(currentAvg, recommended, target)
    elif type == 'Heartrate':
        if 60 <= currentAvg <= 100:
            return "Heart rate is at a normal resting rate."
        return "Average: {0} Target: 60-100".format(currentAvg)
@app.route("/graph")
def displayGraph():
    global updated
    humidityTable, humidityAvg = createTable('Humidity')
    fahrenheitTable, fahrenheitAvg = createTable('Fahrenheit')
    celciusTable, celciusAvg = createTable('Celcius')
    soundTable, soundAvg = createTable('Sound')
    VLTable, VLAvg = createTable('Visible_Light')
    UVTable, UVAvg = createTable('UV_Index')
    StepsTable, StepsAvg = createTable('Steps')
    HeartrateTable, HeartrateAvg = createTable('Heartrate')
    
    recFahrenheit = recommendValue('Fahrenheit', fahrenheitAvg)
    recCelcius = recommendValue('Celcius', celciusAvg)
    recHumidity = recommendValue('Humidity', humidityAvg)
    recSound = recommendValue('Sound', soundAvg)
    recVL = recommendValue('VL', VLAvg)
    recUV = recommendValue('UV', UVAvg)
    recSteps = recommendValue('Steps', StepsAvg)
    recHeartrate = recommendValue('Heartrate', HeartrateAvg)
    
    return """
          <html>
          <head>
            <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
            <script type="text/javascript">
              google.charts.load('current', {'packages':['corechart']});
              google.charts.setOnLoadCallback(drawChart);

              function drawChart() {
              
                var fahrenheitData = google.visualization.arrayToDataTable(""" + str(fahrenheitTable) +""");
                var fahrenheitOptions = {
                title: 'Temperature (Fahrenheit)',
                curveType: 'function',
                legend: { position: 'bottom' }
                };
                var fahrenheitChart = new google.visualization.LineChart(document.getElementById('fahrenheit_chart'));
                
                var celciusData = google.visualization.arrayToDataTable(""" + str(celciusTable) +""");
                var celciusOptions = {
                title: 'Temperature (Celcius)',
                curveType: 'function',
                legend: { position: 'bottom' }
                };
                var celciusChart = new google.visualization.LineChart(document.getElementById('celcius_chart'));
              
                var humidityData = google.visualization.arrayToDataTable(""" + str(humidityTable) +""");
                var humidityOptions = {
                  title: 'Humidity',
                  curveType: 'function',
                  legend: { position: 'bottom' }
                };
                var humidityChart = new google.visualization.LineChart(document.getElementById('humidity_chart'));
                
                var soundData = google.visualization.arrayToDataTable(""" + str(soundTable) +""");
                var soundOptions = {
                  title: 'Sound Levels',
                  curveType: 'function',
                  legend: { position: 'bottom' }
                };
                var soundChart = new google.visualization.LineChart(document.getElementById('sound_chart'));
                
                var vlData = google.visualization.arrayToDataTable(""" + str(VLTable) +""");
                var vlOptions = {
                  title: 'Visible Light',
                  curveType: 'function',
                  legend: { position: 'bottom' }
                };
                var vlChart = new google.visualization.LineChart(document.getElementById('vl_chart'));
                
                var uvData = google.visualization.arrayToDataTable(""" + str(UVTable) +""");
                var uvOptions = {
                  title: 'UV Index',
                  curveType: 'function',
                  legend: { position: 'bottom' }
                };
                var uvChart = new google.visualization.LineChart(document.getElementById('uv_chart'));
                
                var stepsData = google.visualization.arrayToDataTable(""" + str(StepsTable) +""");
                var stepsOptions = {
                  title: 'Steps',
                  curveType: 'function',
                  legend: { position: 'bottom' }
                };
                var stepsChart = new google.visualization.LineChart(document.getElementById('steps_chart'));
            
                var heartrateData = google.visualization.arrayToDataTable(""" + str(HeartrateTable) +""");
                var heartrateOptions = {
                title: 'Heart rate',
                curveType: 'function',
                legend: { position: 'bottom' }
                };
                var heartrateChart = new google.visualization.LineChart(document.getElementById('heartrate_chart'));

                humidityChart.draw(humidityData, humidityOptions);
                fahrenheitChart.draw(fahrenheitData, fahrenheitOptions);
                celciusChart.draw(celciusData, celciusOptions);
                soundChart.draw(soundData, soundOptions);
                vlChart.draw(vlData, vlOptions);
                uvChart.draw(uvData, uvOptions);
                stepsChart.draw(stepsData, stepsOptions);
                heartrateChart.draw(heartrateData, heartrateOptions);
                
              }
            </script>
          </head>
          <body>
            <div id="humidity_chart" style="width: 1500px; height: 600px"></div>
            <center>""" + recHumidity + """</center>
            <div id="fahrenheit_chart" style="width: 1500px; height: 600px"></div>
            <center>""" + recFahrenheit + """</center>
            <div id="celcius_chart" style="width: 1500px; height: 600px"></div>
            <center>""" + recCelcius + """</center>
            <div id="sound_chart" style="width: 1500px; height: 600px"></div>
            <center>""" + recSound + """</center>
            <div id="vl_chart" style="width: 1500px; height: 600px"></div>
            <center>""" + recVL + """</center>
            <div id="uv_chart" style="width: 1500px; height: 600px"></div>
            <center>""" + recUV + """</center>
            <div id="steps_chart" style="width: 1500px; height: 600px"></div>
            <center>""" + recSteps + """</center>
            <div id="heartrate_chart" style="width: 1500px; height: 600px"></div>
            <center>""" + recHeartrate + """</center>
          </body>
        </html>
    """
