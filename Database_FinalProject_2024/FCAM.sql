# LAST UPDATE 5/07/2024
USE `freedb_FCAM_DB`;

drop table if exists machine;
drop table if exists partOrder;
drop table if exists workTicket;
drop table if exists part;
drop table if exists technician;

create table machine(
    machID int auto_increment, 
    machName char(255) NOT NULL,
    PRIMARY	KEY (machID)
    );
    
create table technician(
	techID int auto_increment,
    techName char(255),
    primary key (techID)
    );  

create table workTicket(
	tickID int auto_increment,
    machID int NOT NULL,
    techAssigned int,
    dateCreated date default(curdate()),
    dateAssigned date default(curdate()),
    dateCompleted date,
    PRIMARY KEY (tickID),
    FOREIGN KEY (machID)
		REFERENCES machine(machID)
        on delete cascade,
	FOREIGN KEY (techAssigned)
		REFERENCES technician(techID)
        on delete cascade
    );

create table part(
	partID int auto_increment,
    partName char(255) NOT NULL,
    cost float,
    PRIMARY KEY (partID)
    );
    
create table partOrder(
	tickID int,
    partID int,
    PRIMARY KEY(partID, tickID),
    FOREIGN KEY(partID) 
		REFERENCES part(partID)
		on delete cascade,
	FOREIGN KEY(tickID)
		REFERENCES workTicket(tickID)
        on delete cascade
    );  

--
-- VIEWS AND SOME SUCH
--


drop view if exists techIdView;
drop view if exists incomWorkTicketView;
drop view if exists partOrderNameView;
drop view if exists allWorkTicketView;

create view techIdView as 
	select techID
	from technician;

#incomplete workOrders
create view incomWorkTicketView as
	select workTicket.tickID, workTicket.machID, machine.machName, workTicket.dateCreated, workTicket.dateCompleted, workTicket.techAssigned
    from workTicket, machine
    where workTicket.machID = machine.machID and workTicket.dateCompleted is null;

create view partOrderNameView as
	select partOrder.tickID, partOrder.partID, part.partName
    from partOrder, part
    where partOrder.partID = part.partID;
    
create view allWorkTicketView as
	select workTicket.tickID, workTicket.machID, machine.machName, workTicket.dateCreated, workTicket.dateCompleted, workTicket.techAssigned
    from workTicket, machine
    where workTicket.machID = machine.machID;

#workOrderHistory

#see all machines, mark machines that have active workOrders


--
-- PROCEDURES
--



drop procedure if exists fcam_InsertMachine;
drop procedure if exists fcam_CreateWorkTicket;
drop procedure if exists fcam_InsertWorkTicketPart;
drop procedure if exists fcam_AssignWorkTicket;
drop procedure if exists fcam_CompleteWorkTicket;
drop procedure if exists fcam_DeleteWorkTicket;

delimiter //
USE freedb_FCAM_DB//
create procedure fcam_InsertMachine (in newName varchar(255))
begin
	insert into machine (machName)
    values (newName);
end//
DELIMITER ;

delimiter //
create procedure fcam_CreateWorkTicket (in inMachID int, out outTickID int)
begin
	insert into workTicket (machID) values (inMachID);
        
    select tickID into 'outTickID'
    from workTicket
    Order by tickID desc
    limit 1;
end//

DELIMITER //
create procedure fcam_InsertWorkTicketPart (in inTickID int, in inPartID int)
begin
	insert into partOrder (tickID, partID) value (inTickID, inPartID);
end//

DELIMITER //
create procedure fcam_AssignWorkTicket (in inTickID int, in inTechID int)
begin
	update workTicket 
    set techAssigned = inTechID
    where tickID = inTickID;
end//

DELIMITER //
create procedure fcam_CompleteWorkTicket (in inTickID int)
begin
	update workTicket
    set dateCompleted = curdate()
    where tickID = inTickID;
end//

DELIMITER //
create procedure fcam_DeleteWorkTicket (in inTickID int)
begin
	delete 
    from workTicket 
    where tickID = inTickID;
end//

DELIMITER ;


-- For initial stuff and testing.

insert into technician (techID, techName) value (420, "Bill");
insert into technician (techID, techName) value (690, "Harold Ted");

insert into part (partName, cost) value ("payment device", 150);
insert into part (partName, cost) value ("light", 10);
insert into part (partName, cost) value ("speaker", 100);
insert into part (partName, cost) value ("flipper", 50);
insert into part (partName, cost) value ("plunger", 45);
insert into part (partName, cost) value ("screen", 100);
insert into part (partName, cost) value ("gun and cable", 300);
insert into part (partName, cost) value ("circuit board", 150);
insert into part (partName, cost) value ("steering wheel", 350);
insert into part (partName, cost) value ("shifter", 200);
insert into part (partName, cost) value ("score board", 100);
insert into part (partName, cost) value ("striker", 15);
insert into part (partName, cost) value ("puck", 15);
insert into part (partName, cost) value ("air motor", 350);
insert into part (partName, cost) value ("base board", 150);
