import PySimpleGUI as sg
import asyncio
import aiohttp
import json

api_key = None


sg.theme("Black")
sg.set_options(element_padding=(0, 0))

layout = [
    [sg.Text("Refreshing...", key="status")],
    [
        sg.Push(),
        sg.Text(
            "",
            font=("Helvetica", 20),
            pad=(5, 10),
            justification="center",
            key="hashrate",
        ),
        sg.Push(),
    ],
    [
        sg.Button("Setup", key="setup", button_color=("white", "#001480")),
        sg.Button("Close", button_color=("white", "firebrick4"), key="close"),
    ],
]

window = sg.Window(
    "Running Timer",
    layout,
    no_titlebar=True,
    auto_size_buttons=False,
    keep_on_top=True,
    grab_anywhere=True,
)


async def _get_hashrate():
    window["status"].update("Refreshing...")
    api_url = "https://slushpool.com/accounts/profile/json/btc/"
    global api_key
    key = api_key
    header = {"SlushPool-Auth-Token": f"{key}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, headers=header) as response:
            r = await response.text()
            if r:
                content = json.loads(r)
                hashrate = content["btc"]["hash_rate_scoring"]
                hashrate = round(hashrate / 1000)

                if hashrate > 999:
                    hashrate = f"{round(hashrate / 1000, 2)} PH/s"
                else:
                    hashrate = f"{hashrate} TH/s"

    window["hashrate"].update(hashrate)
    window["status"].update("Current Hashrate:")


async def get_hashrate():
    while True:
        await _get_hashrate()
        await asyncio.sleep(10)


def write_api_key(key):
    global api_key
    api_key = key
    with open("api_key.txt", "w+") as file:
        file.write(key)


def read_api_key():
    with open("api_key.txt", "r") as file:
        key = file.read()
        global api_key
        api_key = key.strip()


async def setup():
    setup_layout = [
        [sg.Text("API Key:"), sg.InputText(key="api_key")],
        [
            sg.Button("Confirm", key="setup_done"),
            sg.Button("Cancel", key="setup_cancel"),
        ],
    ]

    setup_window = sg.Window(
        "Setup",
        setup_layout,
        no_titlebar=True,
        auto_size_buttons=False,
        keep_on_top=True,
        grab_anywhere=True,
    )
    while True:
        event, values = setup_window.read(1)
        if event == sg.WIN_CLOSED or event == "setup_cancel":
            setup_window.close()
            return
        if event == "setup_done":
            write_api_key(values["api_key"])
            await _get_hashrate()
            setup_window.close()
            return
        if event == "__TIMEOUT__":
            pass
        await asyncio.sleep(0)


async def ui():
    window.read(0)
    asyncio.create_task(get_hashrate())
    read_api_key()

    while True:
        event, values = window.read(1)
        if event == sg.WIN_CLOSED or event == "close":
            break

        if event == "setup":
            asyncio.create_task(setup())

        if event == "__TIMEOUT__":
            pass

        await asyncio.sleep(0)


async def main():
    await ui()


if __name__ == "__main__":
    asyncio.run(main())
