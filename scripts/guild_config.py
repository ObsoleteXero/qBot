import asyncpg
import asyncio
import json
from os import getenv
from dotenv import load_dotenv

load_dotenv()


async def joined(guild_id):
    conn = await asyncpg.connect(getenv('DATABASE'))

    row = await conn.fetchrow(
        f'SELECT * FROM guild_config WHERE guild_id = $1', guild_id
    )

    if not row:
        await conn.execute(
            f'INSERT INTO guild_config(guild_id) VALUES ($1)', guild_id
        )

    await conn.close()


async def reaction_roles_add(guild_id, emoji_id, role_id):
    emoji_id = str(emoji_id)
    role_id = str(role_id)
    conn = await asyncpg.connect(getenv('DATABASE'))
    await conn.set_type_codec(
        'json',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog'
    )

    reaction_dict = await conn.fetchval(
        f'SELECT reaction_roles_data FROM guild_config WHERE guild_id = $1', guild_id
    )

    if reaction_dict and emoji_id in reaction_dict:
        await conn.close()
        return False
    elif reaction_dict:
        reaction_dict[emoji_id] = role_id
    else:
        reaction_dict = {emoji_id: role_id}

    await conn.execute(
        'UPDATE guild_config SET reaction_roles_data = $1 WHERE guild_id = $2', reaction_dict, guild_id
    )

    await conn.close()
    return True


async def reaction_roles_remove(guild_id, emoji_id):
    emoji_id = str(emoji_id)
    conn = await asyncpg.connect(getenv('DATABASE'))
    await conn.set_type_codec(
        'json',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog'
    )

    reaction_dict = await conn.fetchval(
        f'SELECT reaction_roles_data FROM guild_config WHERE guild_id = $1', guild_id
    )

    if reaction_dict and emoji_id in reaction_dict:
        reaction_dict.pop(emoji_id)

        await conn.execute(
            'UPDATE guild_config SET reaction_roles_data = $1 WHERE guild_id = $2', reaction_dict, guild_id
        )

        await conn.close()
        return True
    else:
        await conn.close()
        return False


# asyncio.get_event_loop().run_until_complete(joined(602122505410314241))
# asyncio.get_event_loop().run_until_complete(reaction_roles_add(602122505410314241, 628905030463913985, 'dota'))
# asyncio.get_event_loop().run_until_complete(reaction_roles_add(602122505410314241, 486716431837298697, 'gta'))
# asyncio.get_event_loop().run_until_complete(reaction_roles_remove(602122505410314241, 486716431837298697))
