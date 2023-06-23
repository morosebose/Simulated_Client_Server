'''
CIS 41B Spring 2023
Surajit A. Bose
Lab 5 Server
'''

# TODO: let server keep track of individual threads' current dir
# TODO: handle file or directory names with spaces

import socket
import os
import pickle
import threading
import sys

# Constants
HOST = 'localhost'  # Server hostname
PORT = 5113         # Port at which server is listening
MIN_CLIENTS = 1     # Minimum number of clients   
MAX_CLIENTS = 4     # Maximum number of clients 
MIN_TIMEOUT = 3     # Minimum connection timeout in seconds
MAX_TIMEOUT = 30    # Maximum connection timeout in seconds

    
def changeDir(old_path, new_path) :
    '''
    Change the current dir where client is on the server
    
    @param old_path the current dir where the client is
    @param new_path the path to the dir to which the client wants to move    
    @return :
        - if success, tuple with old dir and new dir
        - if failure, tuple with old dir and False
    '''
    try :
        os.chdir(old_path)
        os.chdir(new_path)
        return old_path, os.getcwd()
    except OSError :
        return old_path, False


def listDir(cur_path) :
    '''
    Provide listing of current dir where client is on the server
    
    @param cur_path path where the client currently is on the server
    @return tuple with current path and directory listing at that path
    '''
    return cur_path, os.listdir(cur_path)


def createFile(cur_path, filename) :
    '''
    Create file in current dir where client is on the server, unless 
    file already exists

    @param cur_path path where the client currently is on the server
    @return tuple with cur_path and a Boolean to indicate success or failure
    '''
    os.chdir(cur_path)
    success = True
    try: 
        if os.path.isfile(filename) :
            raise OSError
        f = open(filename, 'a')
        f.close()
    except OSError:
        success = False
    return cur_path, success


def handleConnection(conn, addr, root_dir) :
    '''
    Get and respond to client requests
    
    @param conn the socket to which client is connected
    @param address tuple with the address of the client and the socket
    @param name name of the thread in which the connection is made
    @param root_dir the directory where the server and client start out    
    @return None
    '''
    name = threading.current_thread().name
    print(f'{name} connection to client at port: {PORT}, address: {addr}')
    fun_dict = {'c': changeDir, 'l' : listDir, 'f' : createFile}
    from_client = pickle.loads(conn.recv(1024))
    fun = from_client[0]

    while fun != 'q' :
        if fun == 'g' :
            mesg = root_dir
            print(f'Sending {mesg}')
        else :
            mesg = fun_dict[fun](*from_client[1:])
        conn.send(pickle.dumps(mesg))
        from_client = pickle.loads(conn.recv(1024))
        fun = from_client[0]
    print(f'{name} connection closed by client')
    

def checkArgs(arg_list) :
    '''
    Validate arguments sent in on command line

    @return:
        - if number and type of arguments is correct, empty string
        - if error, string specifying the error        
    '''
    invalid = ''
    try :
        if len(arg_list) > 3 :
            raise RuntimeError
        num = int(arg_list[1])
        timeout = int(arg_list[2])
        if not MIN_CLIENTS <= num <= MAX_CLIENTS :
            invalid = f'Number of clients must be between {MIN_CLIENTS} and {MAX_CLIENTS}'
        elif not MIN_TIMEOUT <= timeout <= MAX_TIMEOUT :
            invalid = f'Timeout must be between {MIN_TIMEOUT} and {MAX_TIMEOUT} seconds'
    except RuntimeError :
        invalid = 'Received too many command line arguments'
    except IndexError :
        invalid = 'Received insufficient number of command line arguments'
    except ValueError :
        invalid = 'Unexpected argument in command line, expected integer'
    return invalid
    
    
def main() :
    '''
    Code driver to start server, manage connections, and handle requests

    Raises SystemExit if arguments passed in on command line are invalid
    
    @return None
    '''
    invalid = checkArgs(sys.argv)
    if invalid :
        print(f'\tUsage: {sys.argv[0]} number_of_clients timeout_in_seconds')
        print(f'\t{invalid}')
        raise SystemExit('\tPlease check command line arguments and try again')
        
    time_out = int(sys.argv[2])
    max_allowed = int(sys.argv[1])
    
    with socket.socket() as to_me :
        root_dir = os.getcwd()
        to_me.bind((HOST, PORT))
        print("Server is up, hostname:", HOST, "port:", PORT)
    
        to_me.listen()
        threads = []
        names = ['First', 'Second', 'Third', 'Fourth']
        try :
            to_me.settimeout(time_out)
            for i in range (max_allowed) :
                cur_name = names[i]
                (conn, addr) = to_me.accept()
                t = threading.Thread(target = handleConnection, args = (conn, addr, root_dir), name = cur_name)
                threads.append(t)
                t.start()
        except socket.timeout :
            print(f'Connection status: {max_allowed} allowed, {i} connected, {max_allowed - i} timed out')
        
        for t in threads: 
            t.join()
    
        print('No open connections, shutting down server')
    

if __name__ == '__main__' :
    main()