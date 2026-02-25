from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from tss_updater import TSSUpdater
import json
import asyncio
from enum import Enum
import time
from datetime import datetime
from urllib.parse import unquote
import os
import sqlite3

'''
Enum list for telemetry categories
'''
class TelemetryCategory(Enum):
    ROVER_TELEMETRY = "rover:pr_telemetry"

    EVA1_TELEMETRY = "eva1:telemetry"
    EVA1_DCU = "eva1:dcu"
    EVA1_IMU = "eva1:imu"

    EVA2_TELEMETRY = "eva2:telemetry"
    EVA2_DCU = "eva2:dcu"
    EVA2_IMU = "eva2:imu"
    
    EVA_STATUS = "eva:status"
    EVA_ERROR = "eva:error"
    EVA_UIA = "eva:uia"

    LTV_LOCATION = "ltv:location"
    LTV_SIGNAL = "ltv:signal"
    LTV_ERRORS = "ltv:errors"

class ConnectionManager:
    def __init__(self):
        '''
        active_connections holds connections for each category in TelemetryCategory
        '''
        self.active_connections = {category.value: set() for category in TelemetryCategory}

    async def connect(self, websocket: WebSocket, category: str):
        '''
        Connects a websocket to receive data from a specific category
        '''
        await websocket.accept()
        if category in self.active_connections:
            self.active_connections[category].add(websocket)

    def disconnect(self, websocket: WebSocket, category: str):
        '''
        Disconnects a websocket from a specific category
        '''
        if category in self.active_connections:
            self.active_connections[category].discard(websocket)

    async def broadcast_category(self, category: TelemetryCategory, message: dict):
        '''
        Sends out data for a specific category

        :param category: The category enum to be broadcast.
        :type category: TelemetryCategory
        :param message: The message (in json format) to be sent.
        :type message: dict
        '''
        category_path = category.value
        if category_path in self.active_connections:
            # Iterate over a snapshot of the current connections to avoid
            # "RuntimeError: Set changed size during iteration" if the set is
            # modified while broadcasting.
            connections_snapshot = list(self.active_connections[category_path])
            for connection in connections_snapshot:
                try:
                    await connection.send_json(message)
                except Exception:
                    # On failure, attempt to close and remove the dead connection
                    try:
                        await connection.close()
                    except Exception:
                        pass
                    self.disconnect(connection, category_path)

class DatabaseManager:
    def __init__(self):
        self.create_time = int(time.time())
        self.create_time_str = datetime.now().strftime("%m-%d_%H-%M-%S")

        base_dir = os.path.dirname(__file__)

        self.logs_dir = os.path.join(base_dir, "logs")

        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

        self.db_path = os.path.join(self.logs_dir, f"tss_data_{self.create_time_str}.db")
    
    def init_db(self):
        '''
        Initializes our database with every enum in TelemetryCategory as a column
        '''
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        '''
        Load all of our categories and create columns for them.
        Then create the query and execute
        '''
        categories = [category.value for category in TelemetryCategory]
        columns = ", ".join(f'"{category}" JSON' for category in categories)

        query = f"CREATE TABLE IF NOT EXISTS telemetry(timestamp TIMESTAMP PRIMARY KEY, {columns})"
        cursor.execute(query)

        connection.commit()
        connection.close()
    
    def update_db(self, timestamp, data):
        '''
        Updates our database with every json related to every column.
        '''
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()


        '''
        Load all of our categories and grab data for each columns.
        Then create the query and execute
        '''
        categories = [category.value for category in TelemetryCategory]

        columns = ", ".join(f'"{category}"' for category in categories)
        placeholders = ", ".join(["?"] * (len(categories) + 1))

        values = [timestamp] + [json.dumps(data.get(category)) for category in categories]

        sql = f"INSERT INTO telemetry (timestamp, {columns}) VALUES ({placeholders})"

        cursor.execute(sql, values)
        connection.commit()
        connection.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    '''
    Run the tss_polling task over the lifespan of the api
    '''
    task = asyncio.create_task(tss_polling())
    try:
        yield
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

app = FastAPI(lifespan = lifespan)

'''
Establish our ConnectionManager and TSSUpdater
'''
manager = ConnectionManager()


@app.websocket("/ws/{category}")
async def websocket_endpoint(websocket: WebSocket, category: str):
    '''
    Creates a websocket connection to a specific category.

    :param category: Our category name in a string
    :type category: str
    '''
    category = unquote(category)
    if category not in manager.active_connections:
        await websocket.close(code = 1003, reason=f"Category: {category} does not exist.")
        return

    await manager.connect(websocket, category)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, category)


async def tss_polling():
    '''
    Obtain TSS IP from environment variable, empty value uses default.
    '''
    ip = input("Enter TSS IP: ")

    tss_updater = TSSUpdater(ip) if ip else TSSUpdater()

    '''
    Setup our database manager to create and update our database
    '''
    database_manager = DatabaseManager()
    database_manager.init_db()

    '''
    Fetches data from our TSSUpdater, reorganizes the data, saves it, and sends it through websockets.
    Also updates a sqlite database.
    '''

    try:
        while True: 
            try:
                raw_rover = await asyncio.to_thread(tss_updater.fetch_data, 0)
                raw_eva = await asyncio.to_thread(tss_updater.fetch_data, 1)
                raw_ltv = await asyncio.to_thread(tss_updater.fetch_data, 2)

                current_time = int(time.time())

                rover_data = json.loads(raw_rover) if isinstance(raw_rover, str) else raw_rover
                eva_data = json.loads(raw_eva) if isinstance(raw_eva, str) else raw_eva
                ltv_data = json.loads(raw_ltv) if isinstance(raw_ltv, str) else raw_ltv

                data = {
                    # Rover Data
                    TelemetryCategory.ROVER_TELEMETRY.value: {
                        "data": rover_data.get("pr_telemetry", {}),
                    },

                    # EVA 1 Data
                    TelemetryCategory.EVA1_TELEMETRY.value: {
                        "data": eva_data.get("telemetry", {}).get("eva1"),
                    },
                    TelemetryCategory.EVA1_DCU.value: {
                        "data": eva_data.get("dcu", {}).get("eva1"),
                    },
                    TelemetryCategory.EVA1_IMU.value: {
                        "data": eva_data.get("imu", {}).get("eva1"),
                    },

                    # EVA 2 Data
                    TelemetryCategory.EVA2_TELEMETRY.value: {
                        "data": eva_data.get("telemetry", {}).get("eva2"),
                    },
                    TelemetryCategory.EVA2_DCU.value: {
                        "data": eva_data.get("dcu", {}).get("eva2"),
                    },
                    TelemetryCategory.EVA2_IMU.value: {
                        "data": eva_data.get("imu", {}).get("eva2"),
                    },

                    # Global EVA Data
                    TelemetryCategory.EVA_STATUS.value: {
                        "data": eva_data.get("status", {}),
                    },
                    TelemetryCategory.EVA_ERROR.value: {
                        "data": eva_data.get("error", {}),
                    },
                    TelemetryCategory.EVA_UIA.value: {
                        "data": eva_data.get("uia", {}),
                    },

                    # LTV Data
                    TelemetryCategory.LTV_LOCATION.value: {
                        "data": ltv_data.get("location", {}),
                    },
                    TelemetryCategory.LTV_SIGNAL.value: {
                        "data": ltv_data.get("signal", {}),
                    },
                    TelemetryCategory.LTV_ERRORS.value: {
                        "data": ltv_data.get("errors", {}),
                    },
                }

                '''
                Update our database with our current data.
                '''
                #database_manager.update_db(current_time, data)
                await asyncio.to_thread(database_manager.update_db, current_time, data)

                '''
                Broadcast all of our data.
                '''
                for category in TelemetryCategory:
                    category_data = data.get(category.value)
                    
                    if category_data is not None:
                        category_data["timestamp"] = current_time # add a timestamp to the message
                        await manager.broadcast_category(category, category_data)

                await asyncio.sleep(1)

            except Exception as err:
                print(f"Unexpected error in polling: {err}")
                await asyncio.sleep(1)
    finally:
        tss_updater.close()