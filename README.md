
<div style="text-align: justify">

# Server and Website Monitor
This repository contains a program that allows monitoring the status of servers and websites based on JSON files that contain the information of each server or website.

## Requirements
To run the program, you need to install the following packages:

- PyQt5: for creating the graphical interface.
- qdarkstyle: for changing the visual style of the interface.
- requests: for making HTTP requests to the websites and checking if they are functioning.
- ping3: for pinging the servers and checking if they are working.

To install these packages, run the following command in the console:

`pip install PyQt5 QDarkStyle requests ping3`

## Execution and Window Closure
Once the packages are installed, to execute the program, simply run the **run_status_bot.py** file. When the interface opens, two tables will be displayed: one for the status of the servers and another for the status of the websites. For each server or website, its name, IP or URL, and current status will be shown, which can be **LOADING**, **ONLINE**, or **OFFLINE**.

When you close the monitor window, the python console will remain open for a few seconds. It is important not to close the python console when this happens, as it will automatically close after a few seconds.

## JSON Files
The servers.json and websites.json files are the JSON files that contain the information of the servers and websites, respectively. Each file should have a list of objects, where each object contains the name and IP or URL of a server or website.

## Functionality
The program also includes a Worker that periodically checks the status of the servers and websites. This Worker runs in a separate thread to avoid blocking the graphical interface. When a change in the status of a server or website is detected, the corresponding table is automatically updated.

To stop the program, simply close the window and wait for the python console to close automatically after a while.

## About the Development
This project includes code snippets generated with the help of the OpenAI Chat GPT model, which is subject to the OpenAI API Terms of Service.

</div>
