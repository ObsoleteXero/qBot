import asyncpg
import asyncio
import json
from os import getenv
from dotenv import load_dotenv

load_dotenv()


async def joined(guild_id):
    conn = await asyncpg.connect(getenv('DATABASE'))

    row = await conn.fetchrow(
        'SELECT * FROM guild_config WHERE guild_id = $1', guild_id
    )

    if not row:
        await conn.execute(
            'INSERT INTO guild_config(guild_id) VALUES ($1)', guild_id
        )

    await conn.close()


async def reaction_messages_status(guild_id):
    conn = await asyncpg.connect(getenv('DATABASE'))
    await conn.set_type_codec(
        'json',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog'
    )

    row = await conn.fetchval(
        'SELECT reaction_roles FROM guild_config WHERE guild_id = $1', guild_id
    )

    await conn.close()
    return row


async def reaction_message_list(guild_id, message_id):
    conn = await asyncpg.connect(getenv('DATABASE'))
    await conn.set_type_codec(
        'json',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog'
    )

    row = await conn.fetchval(
        'SELECT reaction_roles_data FROM guild_config WHERE guild_id = $1', guild_id
    )

    await conn.close()
    if str(message_id) in row:
        return row[f'{message_id}']
    else:
        return False


async def reaction_message_set(guild_id, message_id, msg_data):
    conn = await asyncpg.connect(getenv('DATABASE'))
    await conn.set_type_codec(
        'json',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog'
    )

    reaction_dict = await conn.fetchval(
        'SELECT reaction_roles_data FROM guild_config WHERE guild_id = $1', guild_id
    )

    if reaction_dict:
        reaction_dict[message_id] = msg_data
    else:
        reaction_dict = {message_id: msg_data}

    await conn.execute(
        '''UPDATE guild_config SET reaction_roles = true,
                                   reaction_roles_data = $1 WHERE guild_id = $2''', reaction_dict, guild_id
    )

    await conn.close()

# asyncio.get_event_loop().run_until_complete(joined(602122505410314241))
# x = asyncio.get_event_loop().run_until_complete(reaction_messages_status(602122505410314241))
#asyncio.get_event_loop().run_until_complete(reaction_message_set(602122505410314241, 486716431837298697, {'reaction_id':'role_id'}))


