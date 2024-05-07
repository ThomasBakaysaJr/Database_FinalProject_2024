### Flying Circus Arcade Maintenance app (FCAM) Documentation

Thomas. Miranda. Mark. Pax. Joe

Last Updated: 4/27/2024

---
---
# Summary

The FCAM database and associated app can be used to track the maintenance of the machines of an arcade. The app features the ability to:
* Input Arcade machines
* View work tickets
	- Option to see ALL work tickets or only those that are incomplete.
* Create work tickets
	- Work Tickets will track:
		+ Which machine this ticket was opened for
		+ The date the ticket was created
		+ The date the ticket was assigned
		+ To which technician the ticket was assigned to
		+ The date the ticket was completed
* Assign work tickets to available technicians

---
---

# Tables

---
---

### machine
Table for all Machines in the arcade.

| Attribute 	| Type 		| Description 
| --- 			| --- 		| --- 
| `machID` 		| int 		| Machine ID
| `machName` 	| char(255) | Machine name

---

### part
Table for all Parts avaiable.

| Attribute 		| Type 		| Description 
| --- 				| --- 		| --- 
| `partID` 			| int 		| Part ID
| `partName` 		| char(255) | Part name
| `cost`		 	| float		| Cost of the part

---

### partOrder
Associative table. Relates Work Tickets to the Parts required since one Work Ticket can have multiple parts associated with it.

| Attribute 	| Type 		| Description 	| Foreign Key Reference
| --- 			| --- 		| --- 			| ---
| `tickID` 		| int 		| Ticket ID 	| workticket
| `partID` 		| int 		| Part ID		| part

---

### technician
Table for all technicians

| Attribute 	| Type 			| Description 
| --- 			| --- 			| --- 
| `techID` 		| int 			| Technician ID
| `techName` 	| char(255) 	| Technician's name

---

### workTicket
Table for all Work Tickets, completed or otherwise. Incomplete Work Tickets will have the attribute `dateCompleted` as `NULL`.

| Attribute 		| Type 		| Description 										|Foreign Key Reference
| --- 				| --- 		| --- 												| ---
| `tickID` 			| int 		| Ticket ID 										| 
| `machID` 			| int 		| Machine ID										| machine
| `techAssigned`	| int 		| Tech ID of the assigned technician				| technician
| `dateCreated`		| date 		| Date ticket was created
| `dateAssigned`	| date 		| Date ticket was assigned to a technician [^1]
| `dateCompleted` 	| date 		| Date ticket was completed / closed

---
---

# Views

---
---

### allWorkTicketView
View containing all work tickets. For complete work ticket history.

| Attribute 		| Type 		| Description 
| --- 				| --- 		| --- 
| `tickID` 			| int 		| Ticket ID 
| `machID` 			| int 		| Machine ID
| `machName` 		| char(255) | Machine name
| `dateCreated` 	| date 		| Date ticket was created
| `dateCompleted` 	| date 		| Date ticket was completed / closed
| `techAssigned` 	| int 		| Tech ID of the assigned technician

---

### incomWorkTicketView

View containing all incomplete work tickets.
Where `dateCompleted` is `NULL`

| Attribute 		| Type 		| Description 
| --- 				| --- 		| --- 
| `tickID` 			| int 		| Ticket ID 
| `machID` 			| int 		| Machine ID
| `machName` 		| char(255) | Machine name
| `dateCreated` 	| date 		| Date ticket was created
| 'dateCompleted'	| date		| Date ticket was completed (will be none)
| `techAssigned` 	| int 		| Tech ID of the assigned technician

---

### partOrderNameView

View joining associative table `partOrder` with `part`. Links WORK TICKETS with their associated PARTS and PART NAMES.

| Attribute 	| Type 		| Description 
| --- 			| --- 		| --- 
| `tickID` 		| int 		| Ticket ID 
| `partID` 		| int 		| Part ID
| `partName` 	| char(255) | Part name

---

### techIdView

View of just the technician IDs.

| Attribute 	| Type 		| Description 
| --- 			| --- 		| --- 
| `techID` 		| int 		| Technician ID numbers 


---
---

# Stored Procedures
 WARNING: [^2]

---
---

### fcam_InsertMachine ( newName )

Insert a new machine with the name `newName` into table `machine`.

| Parameter 	| Type 			| Description 
| --- 			| --- 			| --- 
| `newName` 	| varChar(255) 	| Name of the new machine 

---


### fcam_CreateWorkTicket (inMachID, outTickID)

Insert a new workTicket for machine `inMachID` into table `workTicket`. Return this new ticket's `tickID` as `outTickID`.

| Parameter 		| Type 			| Description 
| --- 				| --- 			| --- 
| `inMachID` 		| int	 		| Machine needing a work ticket 
| `outTickID` 		| int 			| The `tickID` of this new work ticket

---

### fcam_AssignWorkTicket (inTickID, inTechID)

Update workTicket, with ticket ID of `inTickID`, so that `techAssigned` is now `inTechID`.

| Parameter 	| Type 			| Description 
| --- 			| --- 			| --- 
| `inTickID` 	| int		 	| `tickID` of Work Ticket to update / assign 
| `inTechID` 	| int		 	| `techID` of a technician who will be assigned

---

### fcam_CompleteWorkTicket (inTickID)

Set a Work Ticket as complete by filling in the `dateCompleted` attribute with the current date.

| Parameter 	| Type 			| Description 
| --- 			| --- 			| --- 
| `inTickID` 	| int		 	| `tickID` of the workTicket to complete 

---

### fcam_InsertTicketPart (inTickID, inPartID)

Insert **ONE** part with partID of `inPartID` for ticketID of `inTickID` into the associative table `partOrder`. To insert multiple parts, even of the same kind, this procedure must be called multiple times.
| Parameter 	| Type 			| Description 
| --- 			| --- 			| --- 
| `inTickID` 	| int		 	| `tickID` of the Work Ticket being added to 
| `inPartID` 	| int		 	| `partID` of the part being added

---

### fcam_DeleteWorkTicket (inTickID)

Delete a work ticket with tickID of 'inTickID'.

| Parameter 	| Type 			| Description 
| --- 			| --- 			| --- 
| `inTickID` 	| int		 	| `tickID` of the Work Ticket to be deleted 


## Notes

[^1]: Currently work tickets should be automatically assigned as they are created in the python application.

[^2]: No safeguards exists at the moment. Our procedures assume that the input data is correct.
