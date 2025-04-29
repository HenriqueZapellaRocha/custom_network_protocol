from user_interface import protocol
import time

protocol.start()

while True:
    time.sleep( 7 )
    print( protocol.get_registers() )
    protocol.talk( "test1", "niceeeee to be here" )