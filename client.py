'''
CIS 41B Spring 2023
Surajit A. Bose
Lab 5 Client
'''
# TODO: let server keep track of individual threads' current dir

import socket
import pickle

# Constants
HOST = '127.0.0.1'  # IP address of client
PORT = 5113         # Port at which to connect to server
TIMEOUT = 3         # Timeout if server connection hangs

def changeResult (recd) :
    '''
    Handle result of request to change directory where client currently is
    
    @param recd tuple with path to old dir and:
        - if success, path to new dir
        - if failure, boolean False
    @return cur_dir path to dir where client currently is
    '''
    if recd[1]:
        cur_dir = recd[1]
        print('New path: ' + cur_dir)
    else:
        cur_dir = recd[0]
        print ('Invalid path')
    return cur_dir


def listResult (recd) :
    '''
    Handle result of request for listing of directory where client currently is
    
    @param recd tuple with path to current dir and listing of dir
    @return cur_dir path to dir where client currently is
    '''
    cur_dir = recd[0]
    if recd[1] :
        print(f'Directories and files found under {cur_dir} :\n-', end = ' ')
        print('\n- '.join(recd[1]))
    else :
        print('Empty directory')
    return cur_dir


def createResult (recd) : 
    '''
    Handle result of request to create new file in dir where client is
    
    @param recd tuple with path to current dir and Boolean indicating success
    @return cur_dir path to dir where client currently is
    '''
    cur_dir = recd[0]
    if recd[1] :
        print(f'File created in {cur_dir}')
    else :
        print('File already exists')
    return cur_dir
        

def handleConnection(s, cur_dir) :
    '''
    Get and validate requests from user, and handle communication with server
    @param s socket at which server is connected
    @param cur_dir path to dir where client currently is
    @return None
    '''
    menu = '''
        c. change directory
        l. list directory
        f. create file
        q. quit
        '''
        
    menu_dict =  {'c': changeResult, 'l' : listResult, 'f' : createResult}
    
    print(menu)
    choice = input('Enter choice: ').lower()
    
    while choice != 'q' :
        if choice not in menu_dict :
            print('Invalid choice, please try again.')       
        else :
            to_send = []
            to_send.append(choice)
            to_send.append(cur_dir)
            if choice == 'c':
                to_send.append(input('Enter path, starting from current directory: '))
            elif choice == 'f' :
                to_send.append(input('Enter filename: '))
            s.send(pickle.dumps(to_send))
            recd = pickle.loads(s.recv(1024))
            cur_dir = menu_dict[choice](recd)
        print(menu)
        choice = input('Enter choice: ').lower()
    s.send(pickle.dumps([choice]))


def main() :
    '''
    Code driver to connect to server and get current directory on server

    @return None
    '''
    with socket.socket() as s :
        s.connect((HOST, PORT))
        print("Client connect to:", HOST, "port:", PORT)
        try: 
            s.settimeout(TIMEOUT)
            s.send(pickle.dumps(['g']))
            cur_dir = pickle.loads(s.recv(1024))
            handleConnection(s, cur_dir)
    
            print('Closed connection to server')
            
        except socket.timeout :
            print('Connection timed out')
        

if __name__ == '__main__' :
    main()