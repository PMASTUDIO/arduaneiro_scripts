import serial
import time
import python_weather
import asyncio
import datetime as dt

from periodic import Periodic

c_ofr = 0

async def periodically(param):
    print(datetime.now(), 'Yay!', param)
    await asyncio.sleep(1)
    print(datetime.now(), 'Done!')

async def get_chance_of_raining():
  # declare the client. format defaults to the metric system (celcius, km/h, etc.)
  async with python_weather.Client() as client:

    # fetch a weather forecast from a city
    weather = await client.get("Sao Paulo")
    hour_now = dt.datetime.now().hour
    print(hour_now)


    today_forecast = None
    for forecast in weather.forecasts:
      if forecast.date == dt.date.today():
        today_forecast = forecast

    if not today_forecast: return

    next_forecast = None
    for hourly in today_forecast.hourly:
      if hourly.time > dt.datetime.now().time():
        next_forecast = hourly

    return next_forecast.chance_of_rain


async def main():
  c_ofr = await get_chance_of_raining()
  p = Periodic(3, periodically, 'Periodically!')
  await p.start()

  with serial.Serial('/dev/ttyACM0', 9600, timeout=1) as arduino:
    time.sleep(0.1)
    if arduino.isOpen():
      try:
        while True:
          #cmd = input("Enter command: (valve): ")
          #arduino.write(cmd.encode())

          while arduino.inWaiting() == 0: pass
          if arduino.inWaiting() > 0:
             try:
               sensorValueStr = arduino.readline().decode('utf-8').rstrip()
             except Exception:
               continue

             sensorValue = float(sensorValueStr)


             print(sensorValue)
             if sensorValue > 500 and c_ofr > 80:
              print("Watering...")
              arduino.write('valve_on'.encode())
             else:
              arduino.write('valve_off'.encode())

             arduino.flushInput()

      except KeyboardInterrupt:
        print("KeyboardInterrupt has been called.")


if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  loop.create_task(main())
  loop.run_forever()

  
