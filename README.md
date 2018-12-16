INTRODUCTION
---------------------------

This Python (2.7.12) email_parser project analyzes metadata from .mail files in a local directory in an attempt to programmatically group them into `conversations`.

REQUIREMENTS and CORE PACKAGES
-----------------------------

pandas 0.23.4
numpy 1.15.3
email.parser

ASSUMPTIONS
-----------------------------

My definition of `conversation`:

---a grouping of emails where...

* a `starter` email 'Subject' does not contain 're:' or 'fw:' and does not contain a number in its 'In-Reply-To' column
* reply emails...
---are in (potentially) direct response to a `starter` email based on the starter email's 'Message-ID' and the reply email's 'In-Reply-To'
---are sent by a recipient of the `starter` email and sent to the sender of the `starter` email 
---have 'Subject' values that contain the 'Subject value from the corresponding `starter` email

--Conversation Grouping Goals by Message-ID:

[1, 2, 3, 6, 7, 8]
[4]
[9, 10, 11]
[12, 13, 14]
[5]
[15]
[16]
[17]

--Meeting #1 conversation #1
* #1 - starter email to 2 recipients
* #2 - reply 1
* #3 - reply 1
* #6 - reply 2, 1 random other person - excited
* #7 - reply 6, 2, 1 meeting location
* #8 - reply 7, 6, 2, 1 follow-up from meeting

--Meeting #1 conversation #2
* #4 - starter email about same meeting - new sender - separate conversation

--Meeting #1 conversation #3
* #9 - starter email about same meeting - follow-up from random other person
* #10 - reply 9 - accidentally removed from thread, response
* #11 - Fw - follow-up from promise in 10

--Having some issues conversation
* #12 - starter email
* #13 - reply 12
* #14 - re-re reply 13, 12

--Meeting #2 conversation
* #17

--Spam (all individual conversations)
* #5
* #15
* #16

PROCESS NOTES
----------------------------
1. Generate a Pandas dataframe from a glob of '.mail' files in local directory via the email.parser library.
(This dataframe can be referenced in this directory: `emails_dataframe.csv`)
2. Identify `starter` emails based on aforementioned assumptions
3. Iterate through starters and compare `Message-ID`, `In-Reply-To`, `Subject`, `From`, and `To` fields with other emails to create conversation groupings

* Final product is a list of lists where each sub-list is a conversation:
[
['1', '2', '3', '6', '7', '8', '11'],
['4'],
['5'],
['9', '10', '11'],
['12', '13', '14'],
['15'],
['16'],
['17']
]
* One-time promotional emails are each grouped into their own sub-lists - they fit the criteria as `starter` emails.
* Email with 'Message-ID' #11 is incorrectly grouped with both Starter #1 and Starter #9, though it should _only_ be grouped with #9

* Tests written with `unittest` - not very familiar with testing Pandas dataframes, but I did my best...



