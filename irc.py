import socket
import sys
import ssl

ctx = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc = ctx.wrap_socket(sock) 
# server = "irc.root-me.org"
# channel = "#root-me_challenge"
server = "irc.freenode.net"
channel = "#RTXDrone"
nick = "SMUSam"
botname = "candy"

def joinchan(chan):
    irc.send(bytes('JOIN' + chan + '\n', 'UTF-8'))
    ircmsg = ""
    while ircmsg.find("Users #RTXDrone") == -1:
        ircmsg = irc.recv(2048).decode('UTF-8')
        ircmsg = ircmsg.strip('\n\r')
        print(ircmsg)
        
def sendmsg(msg, target=channel): # sends messages to the target.
    irc.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))
        
def joinserv(server):
    irc.connect((server, 7070))
    irc.send(bytes('USER ' + nick + ' ' + nick + ' ' + nick + ' ' + nick + '\n', 'UTF-8'))
    irc.send(bytes("NICK "+ nick +"\n", "UTF-8"))
    ircmsg = ""
    while ircmsg.find('Thank you for using freenode!') == -1:
        ircmsg = irc.recv(2048).decode("UTF-8")
        ircmsg = ircmsg.strip('\n\r')
        print(ircmsg)
        
def main():
    joinserv(server)
    joinchan(channel)
    sendmsg('hello?', channel)
    
main()