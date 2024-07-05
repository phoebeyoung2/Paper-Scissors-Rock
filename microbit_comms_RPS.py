import microbit 
import utime    
import radio

# Global constants
ROCK = microbit.Image('00000:09990:09990:09990:00000')
PAPER = microbit.Image('99999:90009:90009:90009:99999')
SCISSORS = microbit.Image('99009:99090:00900:99090:99009')
RPS = (b'R', b'P', b'S')
radio_address = b'0000' #Default value and needs to be changed in the main function
myID = b'00' # Change this to be the same as your assigned micro:bit number

def choose_opponent():
    # """ Return the opponent id from button presses
    #
    # Returns
    # -------
    # byte string:
    #     A two-character byte string representing the opponent ID
    #
    # Notes
    # -------
    # Button A is used to increment a digit of the ID
    # Button B is used to 'lock in' the digit and move on
    # """
    #
    # This function was completed by my lecturer.
    
    # Initialization
    num = [0]*2
    idx = 0
    
    # Main loop over digits
    while idx < len(num):
        microbit.sleep(100)
        # Display only the last character of the hex representation (skip the 0x part)
        microbit.display.show(hex(num[idx])[-1], wait=False)
        # The button increments the digit mod 16, to make sure it's a single hex digit
        if microbit.button_a.was_pressed():
            num[idx] = (num[idx] + 1)%16
        # Show a different character ('X') to indicate a selection
        if microbit.button_b.was_pressed():
            microbit.display.show('X')
            idx += 1
    microbit.display.clear()
    
    # Make sure we return a byte string, rather than a standard string.
    return bytes(''.join(hex(n)[-1] for n in num), 'UTF-8')


def create_address(player_id, opp_id):
    #""" Returns a byte string in the representing the communcation address. 
    # Paramters
    # -------
    # player_id         :byte_string
    #        A two-character byte string representing the player ID
    # opp_id            :byte_string
    #        A two-character byte string representing the opponent ID
    #
    # -------
    # byte string:
    #A 4-character byte string representing the address.
    #The string should be concatenated such that the player with the 
    #larger ID comes second.
    #
    # Author: Phoebe Young
    #"""
    if player_id >= opp_id:
        bytes_string = opp_id + player_id
    else:
        bytes_string = player_id + opp_id
    return bytes_string

def choose_play():
    # """ Returns the play selected from button presses
    #
    # Returns
    # -------
    # byte string:
    #     A single-character byte string representing a move, 
    # as given in the RPS list at the top of the file.
    #
    # Author: Phoebe Young
    # """
    # Initialization
    image_array = [ROCK, PAPER, SCISSORS]
    byte_array = b'RPS'
    idx = 0

    # Continue to loop until the end of array of different plays is reached
    while idx < len(image_array): # 0 1 2 < 3
        microbit.sleep(100)
        image_display = image_array[idx]
        microbit.display.show(image_display) # Display the initial move as rock
        # If button A is pressed, the play is changed
        if microbit.button_a.was_pressed():
            if idx+1 == len(image_array): # idx = 2, end of image array has been reached 
                idx = 0 # Start at the beginning of the image array
            else:
                idx += 1 # Display the next move 
        # If button B is pressed, play is selected
        if microbit.button_b.was_pressed():
            microbit.display.show('X') # Recognises a selection has been made
            return byte_array[idx:idx+1]


def send_choice(play, round_number):
     # """ Sends a message via the radio
    #
    # Parameters
    # ----------
    # play         : byte string
    #     One of b'R', b'P', or b'S'
    # round_number : int
    #     The round that is being played
    #
    # Returns
    # -------
    # int:
    #     Time that the message was sent
    #
    # Author: Phoebe Young
    # """
    #
    time = utime.ticks_ms() # Record the time the message was sent
    choice_message = play + bytes(str(round_number), 'ascii') # concatenate the play and round according to the protocol
    radio.send_bytes(choice_message)
    return time


def send_acknowledgement(round_number):
    # """ Sends an acknowledgement message
    #
    # Parameters
    # ----------
    # opponent_id  : bytes
    #     The id of the opponent
    # round_number : int
    #     The round that is being played
    # """
    #
    # Author: Phoebe Young
    round_number = bytes(str(round_number), 'ascii')
    acknowledgement_message = b'X' + round_number
    radio.send_bytes(acknowledgement_message)


def parse_message(round_number):
    # """ Receive and parse the next valid message
    #
    # Parameters
    # ----------
    # opponent_id  : bytes
    #     The id of the opponent
    # round_number : int
    #     The round that is being played
    #
    # Returns
    # -------
    # bytes :
    #     The contents of the message, if it is valid
    # None :
    #     If the message is invalid or does not need further processing
    #
    # Notes
    # -----
    # This function sends an acknowledgement using send_acknowledgement() if
    # the message is valid and contains a play (R, P, or S), using the round
    # number from the message.
    # 
    # Author: Phoebe Young
    # """
    #
    # 
    # Recieve the message and convert to a string for processing
    recieved_message = radio.receive_bytes()
        
    return_message = None # Default as an invalid message until parsed otherwise
    if recieved_message == None:
        return None 
    else: # A message is received but yet to be validated
        message_string = str(recieved_message) # Turning into a string for indexing
        message_round_number = message_string[3:(len(message_string)-1)]
        message_round_number = int(message_round_number)
        
        if message_round_number == round_number:
            # Checking if the length is valid
            if len(message_string) <= 8:
                valid_1 = 1 # Logical true if it is within a valid length range
            else:
                valid_1 = 0 # Invalid length
        
            
            # Once validated, check if the message is an acknowledgement or a play
            if valid_1 == 1:  
                if (recieved_message[0:1] == b'X'): # message string is acknowledgement
                    return_message = recieved_message[0:1]
                else:
                    send_acknowledgement(round_number)
                    return_message = recieved_message[0:1]
        elif message_round_number < round_number:
            send_acknowledgement(message_round_number)
            return_message = None
        else: 
            return_message = None
    
    return return_message


def resolve(my, opp):
    # """ Returns the outcome of a rock-paper-scissors match
    # Also displays the result
    #
    # Parameters
    # ----------
    # my  : bytes
    #     The choice of rock/paper/scissors that this micro:bit made
    # opp : bytes
    #     The choice of rock/paper/scissors that the opponent micro:bit made
    #
    # Returns
    # -------
    # int :
    #     Numerical value for the player as listed below
    #      0: Loss/Draw
    #     +1: Win
    # int opp_score :
    #     Numerical value for the opponent as listed below
    #      0: Loss/Draw
    #     +1: Win
    #
    # Notes
    # -----
    # Input parameters should be one of b'R', b'P', b'S'
    #
    # Examples
    # --------
    # solve(b'R', b'P') returns 0 (Loss)
    # solve(b'R', b'S') returns 1 (Win)
    # solve(b'R', b'R') returns 0 (Draw)
    #
    # """
    #
    # This function was completed by my lecturer.
    
    # Use fancy list indexing tricks to resolve the match
    diff = RPS.index(my) - RPS.index(opp)
    
    result = [0, 1, 0][diff]
    opp_score = [0,0,1][diff]
    # Display a cute picture to show what happened
    faces = [microbit.Image.ASLEEP, microbit.Image.HAPPY, microbit.Image.SAD]
    microbit.display.show(faces[diff])
    # Leave the picture up for long enough to see it
    microbit.sleep(1000)
    return result, opp_score


def display_score(my_score,opp_score,round_number, times=3):
    # """ Flashes the score on the display
    #     
    # Parameters
    # ----------
    # my_score : int
    #     The current player score
    # opp_score : int
    #     The current opponent score
    # round_number : int
    #     The current round number
    # times : int
    #     Number of times to flash
    #
    # Returns
    # -------
    # None
    #
    # Notes
    # -----
    # Decides if the game is won or lost or drawn.
    # Resolves the game when one player is deemed a winner or loser. 
    # Resets the microbit after the game is complete.
    #
    # This function was completed by my lecturer.

    screen_off = microbit.Image(':'.join(['0'*5]*5))
    microbit.display.show([screen_off, str(my_score)]*times)
    if round_number == 2:
        if my_score == 2:
            for n in range(times):
                microbit.display.scroll("You win!!")
                microbit.display.show(screen_off)
                microbit.sleep(333)
                microbit.reset()
        elif opp_score == 2:
            for n in range(times):
                microbit.display.scroll("You Lose!")
                microbit.display.show(screen_off)
                microbit.sleep(333)
                microbit.reset()
        else:
            pass
    elif round_number == 3:
        if my_score > opp_score:
            for n in range(times):
                microbit.display.scroll("You win!!")
                microbit.display.show(screen_off)
                microbit.sleep(333)
                microbit.reset()
        elif opp_score > my_score:
            for n in range(times):
                microbit.display.scroll("You Lose!")
                microbit.display.show(screen_off)
                microbit.sleep(333)
                microbit.reset()
        elif (opp_score == my_score):
            for n in range(times):
                microbit.display.scroll("You drew!")
                microbit.display.show(screen_off)
                microbit.sleep(333)
                microbit.reset()


def main():
    # '''Main  Control Loop'''
    opponent_id = choose_opponent()
    op_id_string = ''.join(chr(byte) for byte in opponent_id)
    
    radio_address = create_address(myID, opponent_id) 
    decimal_number = int.from_bytes(radio_address, 'little') 
    radio.config(power=6, address = decimal_number)
    radio.on()

    #Initialise score and round
    your_score = 0
    opp_score = 0
    round_number = 1 
    
    while True:
        # Display initial round and player score
        microbit.display.scroll("Round: " + str(round_number),delay=40,monospace=True)
        microbit.display.scroll("Your Score: " + str(your_score),delay=40,monospace=True)
        # Make first move
        choice = choose_play()
        send_time = send_choice(choice, round_number)

        acknowledged, resolved = (False, False)
        microbit.display.show(microbit.Image.ALL_CLOCKS, wait=False, loop=True)
        # Loop until play has been resolved and acknowledged
        while not (acknowledged and resolved):
            
            message = parse_message(round_number)
            #Check that a message has been sent before proceeding
            if message != None:
                message_str = str(message, 'utf-8')

                # If a play has been made
                if message_str[0] != 'X' and not resolved:
                   
                    my_result,opp_result = resolve(choice, message)
                    #Increment scores
                    your_score += my_result
                    opp_score += opp_result
                    display_score(your_score, opp_score, round_number, times = 3)
                    resolved = True
    
                # If an acknowledgement 
                if message_str[0] == 'X':
                    acknowledged = True   
            # If too much time has passed since a play has been made without an acknowledgement 
            else:
                if (utime.ticks_ms() - send_time >= 1000):
                    send_time = send_choice(choice, round_number)
             
        round_number += 1
        continue
                    


# Do not modify the below code, this makes sure your program runs properly!
if __name__ == "__main__":
    main()
    


            
