import pydle
import time

# Simple echo bot.
class MyOwnBot(pydle.Client):
    async def on_connect(self):
         await self.join('#RTXDrone')

    async def on_message(self, target, source, message):
         # don't respond to our own messages, as this leads to a positive feedback loop
         if source != self.nickname:
            await self.message(target, 'test')
            
    async def message(self, message):
        await self.message('#RTXDrone', message)

client = MyOwnBot('MyBot', realname='My Bot')
client.run('chat.freenode.net', tls=True, tls_verify=False)
time.sleep(5)
client.message('custom')