-> 13.0.0.1 

fix method for create vendor bill.


--> 13.0.0.2
in pos receipt not show branches
orders payment not show branches

--> 13.0.0.3
-> Remove pos feature from branch module.


--> 13.0.0.4
-> Solve issue for inventory adjustment when valuation is set automatic.

--> 13.0.0.5
-> Add branch field in picking type related to stock.warehouse and updated the rule from global to user's current branch only for branch user.

--> 13.0.0.6
-> Remove account invoice ref from wizard, update code for sale advanced payment and
pass branch field.

--> 13.0.0.7
-> Call super in all possible methods.
-> Update context all for order lines like sale, purchase, invoice, move and bank statement lines.


Date  30th june 2020
version 13.0.0.8
issue solve:-
	- branch not added in mrp production lines.


date 1st july 2020
version 13.0.0.9
issue solve:-
	- warning generate when selected branch not in allowed branch.


date 3/7/2020
version 13.0.1.0
improvement :-
	- intercompany flow , branch taken from warehouse branch.
	
	
date 7/7/2020
version :- 13.0.2.0
issue solve:-
	- remove class from xpath.


date 10/7/2020
version :- 13.0.2.0
issue solve:-
	- branch id show blank in users.


Date 13th july 2020
version 13.0.4.0
issue solve:-
	- if nothing to given in any user in branch , then user settings not open.


Date 13th july 2020
version 13.0.5.0
issue solve:-
 - pos not open


Date 24th july 2020
version 13.0.5.1
issue solve:-
 - branch domain added properly.


Date 28th july 2020
version 13.0.5.2
issue solve:-
	- multi company record rule conflict with out user record rules , so added global record rule for sale report , account report , purchase report.

Date 28th july 2020
version 13.0.5.3
issue solve:-
	- sale , invoice issue solve
	- multi company record issue solve.
	- branch only select from m2o.



Date 25th aug 2020
version 13.0.5.4
issue solve:-
	- uncomment account statement files from branch module.


Date 8th sep 2020
version 13.0.5.5
improvement :- 
	- update branch domain , only show those branch list which company selected.
	- added new tab for branch in user view.

Date 8th sep 2020
version 13.0.5.6
improvement:-
	- mrp flow now pass branch in account move and stock move