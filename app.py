import sys, discord, configparser, asyncio, requests, json, re

config = configparser.ConfigParser()
config.read('config.ini')

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


def discord_message(forma, data, tag=''):
    message=forma
    daytime=''
    if data['status']['error'] == True:
        message=message.replace('{server_tag}', tag) \
            .replace('{ip}', data['addr'][0]) \
            .replace('{port}', data['addr'][1])
    else:
        sincestart=data['game']['info']['details']['TimeSinceStart']
        daytime+=(str(int(sincestart/60/60%24))) + ' days '
        daytime+=(str(int(sincestart/60%60))) + ' minutes '
        daytime+=(str(int(sincestart%60))) + ' seconds'
        message=message.replace('{server_tag}', tag) \
            .replace('{server_name}',  re.sub(r'<.+?>', '', data['game']['info']['server_name'])) \
            .replace('{map_size}', data['game']['info']['map']) \
            .replace('{player_count}', str(data['game']['info']['player_count'])) \
            .replace('{max_players}', str(data['game']['info']['max_players'])) \
            .replace('{version}', data['game']['info']['version']) \
            .replace('{animals}', str(data['game']['info']['details']['Animals'])) \
            .replace('{plants}', str(data['game']['info']['details']['Plants'])) \
            .replace('{break}', '\r\n') \
            .replace('{address}', data['whois']['addr']['ip'] + ':' + str(data['whois']['addr']['port'])) \
            .replace('{provider}', data['whois']['organization']) \
            .replace('{country}', data['whois']['iso_code']) \
            .replace('{gametime}', daytime)
    return message

class EcoStatus():
    def __init__(self, ip, sid, tag):
        self.sid = sid
        self.tag = tag
        self.ip = ip
        addr=ip.rstrip().split(':')
        r = json.loads(requests.get('http://85.190.150.122/api/eco/' + addr[0] + '/' + addr[1]).text)
        self.response = r
        self.response['addr'] = addr
        self.response['tag'] = tag
        print(r)
        r['game']['info']['server_name'] = re.sub(r'<.+?>', '', r['game']['info']['server_name'])

    def formatted_message(self):
        if self.response['status']['error'] == True:
            return self.ip.rstrip() + ' is unreachable'
        if config.has_option('message_format', str(self.sid)):
            return discord_message(config.get('message_format',str(self.sid)), self.response, self.tag)
        else:
            return discord_message(config.get('message_format','default'), self.response, self.tag)

    def formatted_monitoring(self):
        status='online'
        if self.response['status']['error'] == True:
            status='offline'
        if config.has_option('message_format', str(self.sid) + '_' + status):
            return discord_message(config.get('message_format',str(self.sid) + '_' + status), self.response, self.tag)
        else:
            return discord_message(config.get('message_format','default' + '_' + status), self.response, self.tag)

async def assert_permission():
    if not message.author.server_permissions.manage_server:
        await client.send_message(message.channel, 'Unauthorized')
        return False
    return True

def write_config(config):
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

@client.event
async def on_message(message):
    print('[' + str(message.server.id) + '] ' + message.author.name + ': ' + message.content)
    try:
        command = message.content.split()
        if command[0] == '!addserver':
            if assert_permission():
                if len(command) < 3:
                    await client.send_message(message.channel, 'Command wrong formatted, use: !addserver <name> <ip>:<webport>')
                    return False
                if not config.has_section(str(message.server.id)):
                    config.add_section(str(message.server.id))
                if config.has_option(str(message.server.id), command[1]):
                    await client.send_message(message.channel, 'Server named "'+command[1] + '" already exists. Delete first (!delserver)')
                    return False
                else:
                    config.set(str(message.server.id), command[1], command[2])
                    await client.send_message(message.channel, 'Server added.')
                write_config(config)

        if command[0] == '!delserver':
            if assert_permission():
                if len(command) != 2:
                    await client.send_message(message.channel, 'Command wrong formatted, use: !delserver <name>')
                    return False
                else:
                    if (not config.has_section(str(message.server.id))) or (len(config.items(str(message.server.id))) == 0):
                        await client.send_message(message.channel, 'no servers configured - add one using !addserver <name> <ip>:<webport>')
                        return False
                    else:
                        if not config.has_option(str(message.server.id), command[1]):
                            await client.send_message(message.channel, 'unable to find server ' + command[1])
                        else:
                            config.remove_option(str(message.server.id), command[1])
                            write_config(config)

        if command[0] == '!serverlist':
            if not config.has_section(str(message.server.id)):
                await client.send_message(message.channel, 'No servers configured, sorry')
            else:
                for key in dict(config.items(str(message.server.id))):
                    e = EcoStatus(config.get(str(message.server.id), key), message.server.id, key)
                    await client.send_message(message.channel, e.formatted_message())

        if command[0] == '!setformat':
            if assert_permission():
                if len(command) <= 1:
                    await client.send_message(message.channel,'Please specify the format to use')
                else:
                    config.set('message_format', str(message.server.id), ' '.join(command[1:]))
                    write_config(config)

        if command[0] == '!setmonitoringformat':
            if assert_permission():
                if len(command) <= 2:
                    await client.send_message(message.channel,'Please specify using !setmonitoringformat <online/offline> {tag} {ip}:{port} is offline')
                else:
                    if command[1] == 'online' or command[1] == 'offline':
                        config.set('message_format', str(message.server.id) + '_' + command[1], ' '.join(command[2:]))
                        write_config(config)
                        await client.send_message(message.channel, "Monitoring format for " + command[1] + " servers updated!")
                    else:
                        await client.send_message(message.channel, 'Wrong status defined, only "online" and "offline" are allowed (!setmonitoringformat online {tag} is online!')

        if command[0] == '!subscribemonitoring':
            if assert_permission():
                await client.send_message(message.channel, 'Servers are now monitored')
                config.set('monitoring', message.server.id, message.channel.id)
                write_config(config)

        if command[0] == '!unsubscribemonitoring':
            if assert_permission():
                await client.send_message(message.channel, 'Servers aren\'t monitored anymore')
                config.remove_option('monitoring', message.server.id)
                write_config(config)

        if command[0] == '!status':
            if config.has_section(str(message.server.id)):
                if len(command) == 1:
                    if config.has_option(str(message.server.id), 'main'):
                        e = EcoStatus(config.get(str(message.server.id), 'main'), message.server.id, 'main')
                        await client.send_message(message.channel, e.formatted_message())
                    else:
                        await client.send_message(message.channel, 'main server needs to be added first using !addserver main <ip>:<webport>')
                else:
                    if config.has_option(str(message.server.id), command[1]):
                        e = EcoStatus(config.get(str(message.server.id), command[1]), message.server.id, command[1])
                        await client.send_message(message.channel, e.formatted_message())
                    else:
                        await client.send_message(message.channel, 'server not found.')
    except Exception:
            pass #sentry.captureException(data={'message': message.content, 'discord': message.server.id})

async def monitoring():
    await client.wait_until_ready()
    while True:
        config.read('config.ini')
        for dserver in config.options('monitoring'):
            for server in config.options(dserver):
                state = 'online'
                channel = config.get('monitoring', dserver)
                if config.has_option('states', dserver + '_' + server):
                    state = config.get('states', dserver + '_' + server)
                e = EcoStatus(config.get(dserver, server), dserver, server)
                if e.response['status']['error'] and state == 'offline':
                    continue
                if e.response['status']['error'] == False and state == 'online':
                    continue
                newstate='online'
                if state == 'online':
                    newstate='offline'
                config.set('states', dserver + '_' + server, newstate)
                await client.send_message(discord.Object(id=channel), e.formatted_monitoring())
                print("STATUS CHANGED: " + server)
                write_config(config)
        await asyncio.sleep(10)

client.loop.create_task(monitoring())

client.run(config.get('discord','token'))
