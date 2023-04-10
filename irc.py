import pydle
from datetime import datetime, timedelta

# Simple echo bot.
class MyOwnBot(pydle.Client):
    async def on_connect(self):
         await self.join('#RTXDrone')

    async def on_message(self, target, source, message):
         # don't respond to our own messages, as this leads to a positive feedback loop
         if source != self.nickname:
            SchoolName = 'SMU'
            UGV_ArucoMarkerID = message.split('_')[4]
            timestamp = (datetime.now() - timedelta(hours=5)).strftime("%H:%M:%S")
            # GPS_location_lat = vehicle.location.global_relative_frame.lat
            # GPS_location_lon = vehicle.location.global_relative_frame.lon
            GPS_location_lat = 0
            GPS_location_lon = 0
            await self.message(target, 'RTXDC_2023 {}_UAV_Fire_{}_{}_{}_{}'.format(SchoolName, 
                                                                                   UGV_ArucoMarkerID, 
                                                                                   timestamp, 
                                                                                   GPS_location_lat, 
                                                                                   GPS_location_lon))


client = MyOwnBot('SMU', realname='SMU')
client.run('irc.freenode.net', tls=True, tls_verify=False)