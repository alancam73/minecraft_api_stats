# minecraft_api_stats
AWS Lambda to get Minecraft server stats (online, num-players etc) and push to DynamoDB for querying and BI

### Description
AWS Lambda function to query a Minecraft API to return stats on any Minecraft server hosted on AWS EC2
eg online v offline, num players, version etc

### Pre-requisites
* python 3.7 or higher
* setup the correct IAM permissions - this python script uses EC2, DynamoDB
* create a table in DynamoDB, and define date_time as the primary key

### Environment variables
* dynamodb_tbl : the name of the DynamoDB table to hold the stats
* inst_name : the EC2 Instance name (i-abc123 etc)
* mcsrv_name : The Minecraft Server API with your minecraft server IP & port eg https://api.mcsrvstat.us/2/1.2.3.4:25565

### Example output
```
date_time   p_online   p_players   p_version
2022-03-24 02:40:17	true	{ "online" : { "N" : "0" }, "max" : { "N" : "20" } }	1.18
2022-03-24 03:02:31	true	{ "online" : { "N" : "1" }, "list" : { "L" : [ { "S" : "user1" } ] }, "max" : { "N" : "20" }, "uuid" : { "M" : { "user1" : { "S" : "sgfhdjfgsj-21a8-4cc7-a60a-kjsdfhskfs" } } } }	1.18
```

### Triggers
This lambda can be run standalone or via a trigger eg hourly via an EventBridge rule eg rate(1 hour)

### Caveats
This works fine for viewing in DynamoDB but a subsequent import into QuickSight will not get the online, num-players sub-attributes
A future update will add AWS Glue (Relationalize or Unbox) to flatten the fields for BI
