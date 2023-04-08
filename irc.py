import pydle
import time

# Simple echo bot.
class MyOwnBot(pydle.Client):
    def run(self, *args, **kwargs):
        """ Connect and run bot in event loop. """
        self.eventloop.run_until_complete(self.connect(*args, **kwargs))
        try:
            self.eventloop.run_forever()
        finally:
            self.eventloop.stop()
            
    async def on_connect(self):
         await self.join('#RTXDrone')
         await self.message('#RTXDrone',"RTXDC_2023 [SchoolName]_UAV_Fire_[UGV_ArucoMarkerID]_[timestamp]_[GPS location]")

#     async def on_message(self, target, source, message):
#          # don't respond to our own messages, as this leads to a positive feedback loop
#          if source != self.nickname:
#             await self.message(target, 'test')

client = MyOwnBot('SMU_PI_BOT', realname='My Bot')
client.run('chat.freenode.net', tls=True, tls_verify=False)
