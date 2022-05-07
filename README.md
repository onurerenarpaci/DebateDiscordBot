DebateDiscordBot is a tool for organizing online debate tournaments.

Features:
-	Tabbycat database synchronization,
-	Discord: 
    -   Participant registration 
    -   Auto role assignment and participant renaming
    -   Tournament check-in
    -   Private channel generation for schools and teams
    -   Direct messages containing position and room info for each round 
-	Mail automation for invitations
-	Zoom auto break-out room allocation

First, set up the tournament on Tabbycat and add the teams, judges, and schools.
Add your API key, tournament id, and Tabbycat URL to the environment.
Then set up the discord server for the tournament and create a discord bot from the discord developer dashboard. Afterward, you can configure the discord bot API key, server name, registration channel id, and announcements channel id in the environment.
Then set up a SQL server, initialize the server with init_db.py, and configure the connection on debate_bot.py
To send invitation emails, you can configure and customize the send_emails.py
To create the CSV files for auto Zoom break-out room allocation, use csv_creator.py

Available discord commands:
-	!kayıt \<invite-code> : registrations command for users
-	!checkin : send the check-in message where users can check in by reacting to the message
-	!cutteams : finish the check-in process by removing the teams who did not check-in
-	!beingcut : send an announcement containing a list of teams and judges that are still not checked in
-	!manual_checkin \<user-id> : manually check-in a particular user
-	!motion \<round-number> : start a 1-minute countdown, announce the motion, and start the 15-minute prep time countdown in the announcements channel.
-	!draw : announce the draw of the round, send direct messages containing position and room info 
