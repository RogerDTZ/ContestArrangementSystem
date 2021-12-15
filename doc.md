# Contest Management

* `cas contest create`: Create a folder of a new contest.

  * `name`: Name of the contest, used as the directory.

  * `team_category`: `categoryid` of the target team category.

    You should create a category that holds all teams that participate this contest.

  * `team_id_range`: the team id range. example: `300-399` [300, 400)

  Create a yaml file that stores these information in the folder.

* `cas contest lock`: Prevent any changes.

* `cas contest unlock`: Allow changes.

* `cas contest show`: Show contest information.

# Contestant Management

Contestant section:

* `id`: unique ID
* `name`: name
* `sid`: student id (optional)
* `affiliation`: `externalid` of team_affiliation
* `teamid`: team id
* `seat`: seat info
* `password`: (optional, required when exporting)



* `cas contestant add`: Add a single contestant.

  * `name`: Name of the contestant.
  * `sid`: Student ID (optional, required for school contestants).
  * `affiliation`: `externalid` of team_affiliation, which must exist in the database.
  * `map a seat`: Whether or not to map a seat for this contestant.
  * `generate password`: Generate password for this contestant.

  A unique id is created for the contestant.

  Write a record into file `data/contestants.json`.

  Contestant photo should be placed at `photo/{team_id}.png`.

  Raise exception when:

  * the pair of `(name, sid, affiliation)` conflicts with an existing contestant.
  * a seat mapping is required and no available seat found.
  * no available team id.

* `cas contestant import contestants.tsv`: Import contestants.

  The `tsv` file includes multiple lines. Each line is in the format: `name\tsid\taffiliation`. For example, `czz	12119999	txdy`.

  Raise exception when:

  * the pair of `(name, sid, affiliation)` conflicts with an existing contestant.
  * no available team id.

* `cas contestant remove id`: Remove a contestant with the specified id.

* `cas contestant show id [--password]`: Show information of a contestant (`password` means that whether or not to show the password).

* `cas contestant seat id [--auto]`: Seat a contestant. (Auto seating, or interactive seating)

  * `room`: Room name
  * `seat`: Seat name

  Raise exception if:

  * the contestant is already seated.

* `cas contestant seatall`: Seat all contestants that does not have a seat.

  Raise exception if:

  * no enough available seats.

* `cas contestant unseat [id]`: Unseat a contestant or all contestants (verify twice).

* `cas contestant genpass [id] [--override] [--alphabet=alphabet] [--length=len]`: Generate password for a contestant or all (double check) contestants.

  Raise exception if:

  * some contestant has already have a password. (add `--override` to ignore that)

# Seat Management

* `cas seat import file.tsv`: Import available seats from the given file.

  The `tsv` file should include multiple lines. The format of each line is `room_number\tseat_number`. For example: `TB2-R201	A1`.

  Raise exception if:

  * any imported seat conflicts with an existing seat.

* `cas seat add room_number seat_number`: Add a seat.

  Raise exception if:

  * the new seat conflicts with an existing seat.

* `cas seat remove show seat_id`: Remove a seat.

  Raise exception if:

  * some contestant is using the seat.

* `cas seat show room seat_id`: Check who is using the seat.:

* `cas seat where team_id`: Find out where is a specific team seated.

# Affiliation Management

* `cas affiliation import organizations.tsv`: 

  The `tsv` file should include multiple lines. The format of each line is `organization_fullname\texternalid`. For example: `Southern University of Science and Technology	sustech`.

* `cas affiliation add`: Add a organization.

  * `fullname`: Full name.
  * `externalid`: `externalid` of the organization. **Must be identical to the field in the database!**

  Raise exception if:

  * the new affiliation conflicts with an existing affiliation.

* `cas affiliation remove externalid`: Remove the affiliation.

  Raise exception if:

  * some contestant still belongs to the affiliation.
  
* `cas affiliation show [externalid]`: Show information of an affiliation or all affiliations.

# Export

* `cas export domjudge [contestant_id]`: Generate `accounts.tsv` and `teams.json` for all contestants or a specific contestant.

  Please manually create corresponding affiliation / organization on the DOMJudge. You may need to manually set `externalid` in the database.

  Raise exception if:

  * some contestant is not seated
  * some contestant does not have a password yet

* `cas export contestants [room]`: Export an excel file that contains the basic information (name, sid, organization, teamid, seat) and corresponding seat of all contestants or contestants in a certain room.

  Raise exception if:

  * some contestant is not seated.

  The export time should be included in the filename and the headline.

* `cas export all`: Export all.
