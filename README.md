A simple chatting platform and p2p sharing app

PHASE 1:
- To run this program, open one terminal to launch the server by running
  the command below

  - python server.py UserDetails.txt

  This launches the server and load the user details in the server and
  wait for connection

- The connect to the server, launch another terminal and run the command below

  - python client.py localhost 8080

  This creates the connection to the server at localhost 8080.

  Once in the client, you are require to do 2 things
  - Run REGISTER and enter user_id and password to login

    - When user type REGISTER, it prompts user to enter the client_ID and password
    - Then it will send it to the server for verification

  - Run LOGIN and enter user_id and password to login

    - When user type LOGIN, it prompts user to enter the client_ID and password
    - Then it will send it to the server for verification

  As a user, you are able to 3 things
  1) run MSG command follow by text without ',' will send message to all active client and yourself
  2) run CLIST command will list all active users
  3) run DISCONNECT command will disconnect client from the server


PHASE 2:
- run FPUT command allow user to put name of file to be shared

  - It will prompt user to enter filename and wrap together with IP_address and PORT together
  - The packet will then send to the server

- run FLIST command will allow user to get the name of file and file id that is available

- run FGET command will allow user to get the file from the other client

  - It will prompt user to enter fileID
  - The packet will then send to the server
