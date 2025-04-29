from user_interface import protocol
import time

protocol.start()

while True:
    time.sleep( 1 )
    print( protocol.get_registers() )
    protocol.talk( "test1", "niceeeee to be here" )