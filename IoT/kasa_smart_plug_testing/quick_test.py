import asyncio
import sys
from kasa.iot import IotPlug

async def get_plug_data(dev):

    loop_count = 0

    while loop_count < 5:

            await dev.update()
            loop_count += 1 

            # just put the feature you want to test here
            # this is just an example
            print(dev.emeter_realtime.power)

            await asyncio.sleep(5)


def main():

    device = IotPlug('plug_ip_address')

    # start device monitoring
    asyncio.run(get_plug_data(device))


if __name__ == "__main__":
    main()
