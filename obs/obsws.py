import asyncio

from obswsrc import OBSWS
from obswsrc.requests import ResponseStatus, StartRecordingRequest, StopRecordingRequest


async def main(x, w, p, c):
    server = str(x)
    wall = int(w)
    password = str(p)
    command = str(c)

    async with OBSWS(server, wall, password) as obsws:

        # Send request to OBS server to start or stop the recording.
        if command is 'start':
            response = await obsws.require(StartRecordingRequest())
        elif command is 'stop':
            response = await obsws.require(StopRecordingRequest())
        else:
            pass

        # Check if everything is OK
        if response.status == ResponseStatus.OK:
            return "Recording has started"
        else:
            return "Couldn't start the recording! Reason:", response.error


def obs_connector(server, wall, password, command):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(server, wall, password, command))
    return True
