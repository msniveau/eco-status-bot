# eco-status-bot
pretty simple, just clone the repo, rename config.ini.dist to config.ini, put in your discord token and thats it, just run the app.py

if you don't know how to create a discord token you may want to have a look here:
https://github.com/msniveau/discord_cleverbot

ecoforum thread:
http://ecoforum.strangeloopgames.com/topic/4084/eco-server-discord-status-bot

Supported commands:
requires the permission to edit the discord server settings:
```txt
!addserver           - !addserver <name> <ip>:<webport>            - adds a server to the serverlist
!delserver           - !delserver <name>                           - deletes a server from the serverlist
!setformat           - !setformat {server_name}                    - variables / examples below
!subscribemonitoring                                               - subscribe for status change-reports (online / offline)
!unsubscribemonitoring                                             - stop reprting status changes (online / offline) 
!setmonitoringformat - !setmonitoringformat offline {ip} offline   - defines the monitoring format
!setname             - !setname somename                           - sets the discord clients name
```
no permission check:
```txt
!serverlist   - !serverlist                          - lists all servers added
!status       - !status [name]                       - if no name provided the server named "main" will be used
```

Formatting examples / variables for !status !serverlist and monitoring (if online):
```text
    {server_tag}           => tag of the server
    {server_name}          => Server name
    {map_size}             => Map size
    {player_count}         => Current player count
    {max_players}          => Max players / player profiles available on the server
    {version}              => Eco version
    {animals}              => Animal count
    {plants}               => Plant count
    {provider}             => Hosting provider (company owning IP)
    {country}              => Country (location of IP)
    {address}              => IP + Port
    {ip}                   => IP
    {port}                 => Port
    {gametime}             => time since the server is running (ingame)
    {break}                => Line break
```


Usage example:
```!setformat Server online! Servername: {server_name}{break}Players online: {player_count}  ```

Print everyting:
```!setformat server_name: {server_name}{break}map_size: {map_size}{break}player_count: {player_count}{break}max_players: {max_players}{break}version: {version}{break}animals: {animals}{break}plants: {plants}{break}provider: {provider}{break}country: {country}{break}address: {address}{break}gametime: {gametime}```

Formatting examples / variables for monitoring:
```text
    {server_tag}          => tag of the server
    {ip}                  => IP of the server
    {port}                => Port of the server
```
Examples:
```!setmonitoringformat online {server_tag} with the ip {ip} is unavailable!```
```!setmonitoringformat online {server_tag} is up and running on version {version}! current gametime: {gametime}```
