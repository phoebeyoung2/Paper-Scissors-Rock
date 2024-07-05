This was a project where the objective was to implement Rock-Paper_Scissors on a microbit. The microbit sends messages as byte strings via the radio. The file 'microbit_comms_RPS.py' contains all functions written for the project.

I implemented functions that:
- Selected an opponent
- Establishing a radio address the two microbits can use to communicate
- Sending a message containing the move (Rock, Paper or Scissors) and the round number
- Sends an acknowledgement upon recieving a message
- Parse incoming messages
- Using all of the functions to create game play
