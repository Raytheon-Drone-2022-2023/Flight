import socket
import sys

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "irc.root-me.org"
channel = "#root-me_challenge"
nick = "SMUSam"
botname = "candy"

def joinchan(chan):
    irc.send(bytes('JOIN' + chan + '\n', 'UTF-8'))
    ircmsg = ""
    while ircmsg.find("End of /NAMES list.") == -1:
        ircmsg = irc.recv(2048).decode('UTF-8')
        ircmsg = ircmsg.strip('\n\r')
        print(ircmsg)
        
def sendmsg(msg, target=channel): # sends messages to the target.
    irc.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))
        
def joinserv(server):
    irc.connect((server, 6667))
    irc.send(bytes('USER ' + nick + ' ' + nick + ' ' + nick + ' ' + nick + '\n', 'UTF-8'))
    irc.send(bytes("NICK "+ nick +"\n", "UTF-8"))
    # ircmsg = ""
    # while ircmsg.find('MODE SMU') ==-1:
    #     ircmsg = irc.recv(2048).decode("UTF-8")
    #     ircmsg = ircmsg.strip('\n\r')
    #     print(ircmsg)
        
def main():
    joinserv(server)
    joinchan(channel)
    sendmsg('hello?', botname)
    
main()