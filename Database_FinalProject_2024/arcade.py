# import csv
import os       # needed for clear screen   
import sys
from turtle import clear
import mysql.connector

#Turned on autocommit, starts of as FALSE by default
cnx = mysql.connector.connect(user='freedb_FcamUser', password='eqxkFmcDr6PE9#*',
                              host='sql.freedb.tech',
                              database='freedb_FCAM_DB',
                              autocommit = True)

#used for the text inputs
backOutText = " Press Enter to go back: "

def main():
    menu()

def menu():
    loop = 1
    choice = 0
    #menu selection loop
    while loop == 1:
        ClearConsole()

        print("Flying Circus Arcade Maintenance")
        choice = input("""
                       1: Create Ticket
                       2: View Tickets
                       3: Update Tickets
                       4: Insert Machine
                       -----------------
                       5: View Machines
                       6: View Parts
                       7: View Technicians
                       -----------------
                       Q: Quit
                       -----------------
                       D: Developer Tools
                       
                       Please Input Choice: """)
        if choice == "1":
            createTicket()
        elif choice == "2":
            viewTickets()
        elif choice == "3":
            updateTicketsMenu()
        elif choice == "4":
            insertMachine()
        elif choice == "5":
            viewAllMachines()
        elif choice == "6":
            viewAllParts()
        elif choice == "7":
            viewAllTechnicians()
        elif choice.lower() == "d":
            devTools()
        elif choice.lower() == 'q':
            cnx.close()
            ClearConsole()
            print("Goodbye!")
            sys.exit
            loop = 0
        else:
            print("Invalid Selection")
            print("Please try again.")
            
#See all current functions. Self explanatory
def viewAllMachines():
    ClearConsole()
    cursor = cnx.cursor()
    query = "select machID, machName from machine"
    
    print("Machine #, Machine name")
    cursor.execute(query)
    for (machID, machName) in cursor:
        print ("NO. {}, NAME: {}".format(machID, machName))    
        
    cursor.close()        
    WaitForKeypress()
    
def viewAllParts():
    ClearConsole()
    cursor = cnx.cursor()
    query = "select partID, partName, cost from part"
    
    cursor.execute(query)
    for (partID, partName, cost) in cursor:
        print ("NO. {}, NAME: {},   ${}".format(partID, partName, cost))
        
    cursor.close()
    WaitForKeypress()

#standalone function to clear and list just the technicians
def viewAllTechnicians():
    ClearConsole()
    listTechnicians()
    WaitForKeypress()

# helper function, just lists the technicians, doesn't clear or wait
def listTechnicians():
    cursor = cnx.cursor()
    query = "select techID, techName from technician"
    
    cursor.execute(query)
    for (techID, techName) in cursor:
        print ("ID: {}, NAME: {}".format(techID, techName))       
        
    cursor.close()

# insert one machine into the database
def insertMachine():
    ClearConsole()
    
    returnTup = checkInput("What is this machine's name?: " + backOutText, False)
    if not returnTup[0]:
        return
    newName = returnTup[1]
    
    cursor = cnx.cursor()
    args = (newName,)
    cursor.callproc("fcam_InsertMachine", args)
    
    cursor.close()    
    print ("Machine \"" + newName + "\" has been added.")
    WaitForKeypress()


'''
Creates a work ticket for a machine ID. Ask if user wishes to assign it immediately or wait.

TO DO:
Loop asking for parts needed for the work ticket
call "fcam_InsertTicketPart(inTickID, inPartID), you can use the 
'''
def createTicket(): ####################################################
    ClearConsole()

    returnTup = checkInput("Enter Machine ID. " + backOutText, True)
    if not returnTup[0]:
        return
    
    inMachID = returnTup[1]
    outTickID = 0
    endText = "\n\nWork ticket created."

    cursor = cnx.cursor()
    args = (inMachID, outTickID)
    resultArgs = cursor.callproc("fcam_CreateWorkTicket", args)    
    cursor.close()
    
    print("Ticket # " + str(resultArgs[1]) + " has been created.") 

    print("List of Current Parts:")
    # copied from viewAllParts above, just minus the waiting
    cursor = cnx.cursor()
    query = "select partID, partName, cost from part"
    
    cursor.execute(query)
    for (partID, partName, cost) in cursor:
        print ("NO. {}, NAME: {},   ${}".format(partID, partName, cost))
        
    cursor.close()

    insertWorkTicketPart(resultArgs[1])
    print("Would you like to assign this Work Ticket to a technician now?")
    if WaitForYesNo():
        assignTech(resultArgs[1])
        endText += " Work Ticket assigned to technician."
    else:
        endText += " Work Ticket NOT assigned to a technician."


    print(endText)
    WaitForKeypress()
    
def assignTech(inTickID):  ################################################

    # If the tickID is a negative number, that means we want to pick the ticket to assign first
    # Otherwise that means we're coming straight from the createTicket function and
    # have a ticket in mind already.
    if inTickID < 0:
        print("Available tickets are as follows.")
        listTickets(True)
        
        inPrompt = "Which ticket would you like to assign?" + backOutText
        returnTup = checkInput(inPrompt, True)
    
        if not returnTup[0]:
            return    
        inTickID = returnTup[1]

    listTechnicians()
    while True:
        try:
            inTechID = int(input("Enter tech ID: "))
            cursor = cnx.cursor()
            args = (inTickID, inTechID)
            cursor.callproc("fcam_AssignWorkTicket", args) 

            cursor.close()
            break
        except:
            print("Please input valid technician ID.")
            continue

    ClearConsole()

def insertWorkTicketPart(inTickID):
    loopVar = 'g'
    while loopVar != 'q':
        try:
            inPartID = int(input("Enter part ID: ")) # remove "required"
        except:
            print ("Please enter a valid part number.")
            continue
        #the try is to catch invalid partIDs (such as violating foreign keys)
        try:
            cursor = cnx.cursor()
            args = (inTickID, inPartID)
            cursor.callproc("fcam_InsertWorkTicketPart", args)
            cursor.close
        except:
            print("Please input a valid part number.")
            continue
        loopVar = input("Enter y to enter another part or q to quit: ")


def viewTickets():
    ClearConsole()
    #Give option to only see tickets that are in progress
    print("List only incomplete tickets?")
    onlyIncom = WaitForYesNo()    
        
    ClearConsole()    
    listTickets(onlyIncom)

    WaitForKeypress()
    ClearConsole()
    
# helper function that lists all the tickets.
# "onlyIncom": If true, list only the incomplete tickets.
# !!! WILL NOT CLEAR SCREEN !!!    
def listTickets(onlyIncom):
    
    #designate which view to use
    if onlyIncom:      
        view = 'incomWorkTicketView'
    else:
        view = 'allWorkTicketView'
        print ("NONE in Completed Date designates an INCOMPLETE work ticket\n")
        WaitForKeypress()
        
    # use "view" to get the data needed from the correct view, this way we don't have to parse through
    # the entirety for the ticket table.
    cursor = cnx.cursor()
    query = "select tickID, machID, machName, dateCreated, dateCompleted, techAssigned from " + view
    cursor.execute(query)
    for (tickID, machID, machName, dateCreated, dateCompleted, techAssigned) in cursor:
        print ("""\t\tTICKET NO. {}
                FOR MACHINE NO.{}, NAME: {}
                DATE CREATED: {}, DATE COMPLETED: {}
                ASSIGNED TO TECH NO. {}
                WITH PARTS: """.format(tickID, machID, machName, dateCreated, dateCompleted, techAssigned), end = " ")
        cursor2 = cnx.cursor()
        query = "select partName from partOrderNameView where tickID = %s"
        cursor2.execute(query, (tickID,))
        for (partName) in cursor2:
            print("{}".format(partName), end = " ")
    
    print()
    cursor.close()
    return


def updateTicketsMenu():
    loop = 1
    choice = 0
    #update tickets menu
    while loop == 1:
        ClearConsole()
        print("Update Tickets")
        choice = input("""
                       1: Assign Work Ticket to a Technician
                       2: Mark Work Ticket as Complete
                       3: Delete Work Ticket
                       4: View all Work Tickets
                       Q: Back
                       
                       Please Input Choice: """)
        if choice == "1": #Assign work ticket
            #The -1 signals to the function that we want to select a work ticket to assign
            assignTech(-1)
        elif choice == "2": #Mark work ticket as complete
            completeWorkTicket()
        elif choice == "3": #Delete work ticket
            deleteWorkTicket()
        elif choice == "4": #View all work tickets
            viewTickets()
        elif choice.lower() == 'q':
            loop = 0
        else:
            print("Invalid Selection")
            print("Please try again.")    

# Complete a work ticket. Automatically marks today as the date it was completed
def completeWorkTicket():
    ClearConsole()
    
    print("Current incomplete tickets.\n\n")
    listTickets(True)
    inPrompt = "Input Ticket No. to mark as complete. " + backOutText.strip(": ") + ".\nComplete Ticket No: "
    
    returnTup = checkInput(inPrompt, True)
    
    if not returnTup[0]:
        return    
    inTickID = returnTup[1]
    
    cursor = cnx.cursor()
    
    args = (inTickID,)
    cursor.callproc("fcam_CompleteWorkTicket", args)

    cursor.close()
    ClearConsole()

def deleteWorkTicket():
    ClearConsole()

    print("Delete Work Ticket")

    while True:
        try:
            print("Enter nothing to return")
            inTickID = int(input("Ticket no. to be deleted: "))

            cursor = cnx.cursor()
            args = (inTickID,)
            cursor.callproc("fcam_DeleteWorkTicket", args)
            cursor.close

            print ("Ticket no. " + str(inTickID) + " deleted.")
            WaitForKeypress()
            break
        except:
            break

def WaitForKeypress():
    input("Press Enter to continue...")


def ClearConsole():
   os.system('cls')        # windows
    #os.system('clear')      # linux, macos

def WaitForYesNo():
    while 1 == 1:
        answer = input("Y/N : ")
        if answer.lower() == "y" or answer.lower() == "yes":
            return True
        elif answer.lower() == "n" or answer.lower() == "no":
            return False
        else:
            print("Invalid choice.")


# helper function to check if the user input is something or just white space. 
# uses inPrompt as the input prompt text. 
# intOnly determines if the input MUST be an int; Will repeat until either white space or
# an int is used as an input
# RETURN IS A TUPLE, INDEX 0 IS FALSE IF NOTHING WAS ENTERED, TRUE OTHERWISE            
def checkInput(inPrompt, intOnly):
    while True:
        userInput = input(inPrompt)
        # check if userInput is a valid input. strip() will return FALSE if there is only white space
        if not userInput.strip():
            return [False, ""]
        
        # If intOnly is true, makes sure that the user input is an int.
        if (intOnly):            
            try:
                assert int(userInput)
            except ValueError:
                print("Input not an int. Please try again.\n")
                continue
            else:
                return [True, userInput]
        else:
            return [True, userInput]

'''
# DEV TOOLS FROM HERE ON DOWN
# Technically no one should be able to access these commands. For testing purposes.   
 ______   _______  __   __    _______  _______  _______  ___      _______ 
|      | |       ||  | |  |  |       ||       ||       ||   |    |       |
|  _    ||    ___||  |_|  |  |_     _||   _   ||   _   ||   |    |  _____|
| | |   ||   |___ |       |    |   |  |  | |  ||  | |  ||   |    | |_____ 
| |_|   ||    ___||       |    |   |  |  |_|  ||  |_|  ||   |___ |_____  |
|       ||   |___  |     |     |   |  |       ||       ||       | _____| |
|______| |_______|  |___|      |___|  |_______||_______||_______||_______|   
'''


def devTools():
    loop = 1
    choice = 0
    #DEV TOOLS selection loop
    while loop == 1:
        ClearConsole()
        print("*** DEV COMMANDS ***")
        choice = input("""
                       1: Create 100 machines of four types
                       2: View all machines
                       Q: Back
                       
                       Please Input Choice: """)
        if choice == "1":
            devInsertMachines()
        elif choice == "2":
            viewAllMachines()
        elif choice.lower() == 'q':
            loop = 0
        else:
            print("Invalid Selection")
            print("Please try again.")
            
def devInsertMachines():
    ClearConsole()
    print ("Adding machines. This may take a minute.")
    cursor = cnx.cursor()
    # pinball
    for x in range(1,26):
        args = ( "Pinball " + str(x), )
        cursor.callproc("fcam_InsertMachine", args)

    # shooters
    for x in range(1,26):
       args = ("Shooter " + str(x), )
       cursor.callproc("fcam_InsertMachine", args)

    # air hockey
    for x in range(1,26):
        args = ("Air Hockey Table " + str(x), )
        cursor.callproc("fcam_InsertMachine", args)

    # racing
    for x in range(1,26):
        args = ("Racing " + str(x) ,)
        cursor.callproc("fcam_InsertMachine", args)
        
    print("DEV TOOL: Added 100 machines")
    WaitForKeypress()
         

main()