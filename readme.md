# ANYPOINT MONITOR

## Prerequisites
Before using this Python application, please make sure you have the following prerequisites installed:
- Python 3: This application requires Python 3 or later version. You can download the latest version of Python from the official website: https://www.python.org/downloads/.

- Anypoint CLI: This application also requires the Anypoint Command Line Interface (CLI) to interact with the Anypoint Platform. You can download and install the Anypoint CLI by following the instructions provided in the official documentation: https://docs.mulesoft.com/runtime-manager/anypoint-platform-cli


## Installation
To install this application, please follow the steps below:
- Clone the repository to your local machine: git clone https://github.com/Neo-Integrations/anypoint-monitor-py.git
- Navigate to the project directory: `cd anypoint-monitor-py`
- Install the required Python packages: `pip install -r requirements.txt`
- Start the application by running the following command: `python app.py`
- If you have `anypoint-cli` credential files are configuired in `$HOME/.anypoint/` directory, please rename them to something else so that the application runs with its own authentication.

## Configuration
Before you run the application you will need to modify the `resources/cpnfig-dev.yaml` to set the correct authentication strategy (`auth.strategy`)  with Anypoint. Valid values are `userPassword`, `refreshToken` and `connectedApp`. When you select any one of them you will need pass the right environment variables.

- **userPassword:** If you select `userPassword` as the `auth.strategy` in `resources/cpnfig-dev.yaml`, you will need to pass following environmental variables. In case of unix like system you can declared the env variables like below:
    ```
        export ANYPOINT_USERNAME="your_anypoint_user_name"
        export ANYPOINT_PASSWORD="your_anypoint_password"

    ```
- **connectedApp:** If you select `connectedApp` as the `auth.strategy` in `resources/cpnfig-dev.yaml`, you will need to pass following environmental variables. In case of unix like system you can declared the env variables like below:
    ```
        export ANYPOINT_CLIENT_ID="anypoint_connectedapp_client_id"
        export ANYPOINT_CLIENT_SECRET="anypoint_connectedapp_client_secret"
    ```
- **refreshToken:** If you select `refreshToken` as the `auth.strategy` in `resources/cpnfig-dev.yaml`, you will need to pass following environmental variables. In case of unix like system you can declared the env variables like below:
    ```
        export ANYPOINT_CLIENT_ID="anypoint_connectedapp_client_id"
        export ANYPOINT_CLIENT_SECRET="anypoint_connectedapp_client_secret"
        export ANYPOINT_REFRESH_TOKEN="anypoint_connectedapp_refresh_token"
    ```

## Running the application
To run the application, run the followings command from your selected command line tool:
- To gather CloudHub application usage, run: `python3 chv1-application-usage.py`
- To gather API Usage report, run: `python3 anypoint-api-usage.py`