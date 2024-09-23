from datetime import datetime, timedelta, timezone
from dateutil import parser
from time import time
from urllib.parse import unquote, quote

from json import dump as dp, loads as ld
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw import types

import asyncio
import random
import string
import brotli
import base64
import secrets
import uuid
import aiohttp
import json

from .agents import generate_random_user_agent
from .headers import headers
from .helper import format_duration

from bot.utils.random import (
    fake,
    random_fingerprint, generate_f_video_token, get_random_resolution,
    get_random_timezone, get_random_timezone_offset, get_random_plugins,
    get_random_canvas_code, get_random_fingerprint, generate_random_data,
    random_logger_bytes, random_choices
)

from bot.config import settings
from bot.utils import logger
from bot.utils.logger import SelfTGClient
from bot.exceptions import InvalidSession

self_tg_client = SelfTGClient()

class Tapper:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.user_id = 0
        self.username = None
        self.first_name = None
        self.last_name = None
        self.fullname = None
        self.start_param = None
        self.peer = None
        self.first_run = None

        self.session_ug_dict = self.load_user_agents() or []

        headers['User-Agent'] = self.check_user_agent()

    async def generate_random_user_agent(self):
        return generate_random_user_agent(device_type='android', browser_type='chrome')

    def info(self, message):
        from bot.utils import info
        info(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    def debug(self, message):
        from bot.utils import debug
        debug(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    def warning(self, message):
        from bot.utils import warning
        warning(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    def error(self, message):
        from bot.utils import error
        error(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    def critical(self, message):
        from bot.utils import critical
        critical(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    def success(self, message):
        from bot.utils import success
        success(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    def save_user_agent(self):
        user_agents_file_name = "user_agents.json"

        if not any(session['session_name'] == self.session_name for session in self.session_ug_dict):
            user_agent_str = generate_random_user_agent()

            self.session_ug_dict.append({
                'session_name': self.session_name,
                'user_agent': user_agent_str})

            with open(user_agents_file_name, 'w') as user_agents:
                json.dump(self.session_ug_dict, user_agents, indent=4)

            logger.success(f"<light-yellow>{self.session_name}</light-yellow> | User agent saved successfully")

            return user_agent_str

    def load_user_agents(self):
        user_agents_file_name = "user_agents.json"

        try:
            with open(user_agents_file_name, 'r') as user_agents:
                session_data = json.load(user_agents)
                if isinstance(session_data, list):
                    return session_data

        except FileNotFoundError:
            logger.warning("User agents file not found, creating...")

        except json.JSONDecodeError:
            logger.warning("User agents file is empty or corrupted.")

        return []

    def check_user_agent(self):
        load = next(
            (session['user_agent'] for session in self.session_ug_dict if session['session_name'] == self.session_name),
            None)

        if load is None:
            return self.save_user_agent()

        return load

    async def get_tg_web_data(self, proxy: str | None) -> str:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            with_tg = True

            if not self.tg_client.is_connected:
                with_tg = False
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            if settings.USE_REF == True and settings.REF_ID is not None:
                ref_id = settings.REF_ID
            else:
                ref_id = 'ref_355876562'

            self.start_param = random_choices([ref_id, 'ref_355876562'])

            peer = await self.tg_client.resolve_peer('Binance_Moonbix_bot')
            InputBotApp = types.InputBotAppShortName(bot_id=peer, short_name="start")

            web_view = await self.tg_client.invoke(RequestAppWebView(
                peer=peer,
                app=InputBotApp,
                platform='android',
                write_allowed=True,
                start_param=self.start_param
            ), self)

            headers['Referer'] = f"https://www.binance.com/en/game/tg/moon-bix?tgWebAppStartParam={self.start_param}"

            auth_url = web_view.url

            tg_web_data = unquote(
                string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0])

            try:
                if self.user_id == 0:
                    information = await self.tg_client.get_me()
                    self.user_id = information.id
                    self.first_name = information.first_name or ''
                    self.last_name = information.last_name or ''
                    self.username = information.username or ''
            except Exception as e:
                print(e)

            if with_tg is False:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(
                f"<light-yellow>{self.session_name}</light-yellow> | Unknown error during Authorization: {error}")
            await asyncio.sleep(delay=3)

    async def login(self, http_client: aiohttp.ClientSession, tg_data):
        try:
            payload = {
                "queryString": tg_data,
                "socialType": "telegram"
            }

            response = await http_client.post(
                "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/third-party/access/accessToken",
                json=payload
            )

            data = await response.json()

            if data['code'] == '000000':
                access_token = data['data']['accessToken']
                refresh_token = data['data']['refreshToken']

                self.success(f"Get access token successfully")

                return access_token, refresh_token
            else:
                self.warning(f"{self.session_name} | Get access token failed: {data}")
        except Exception as e:
            self.error(f"Error occurred during login: {e}")
    async def complete_task(self, http_client: aiohttp.ClientSession, task: dict):
        task_ids = [task['resourceId']]

        payload = {
            "referralCode": "null",
            "resourceIdList": task_ids
        }

        response = await http_client.post(
            "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/complete",
             json=payload
        )
        data = await response.json()

        if data['success']:
            return "done"
        else:
            return data['messageDetail']

    async def setup_account(self, http_client: aiohttp.ClientSession):
        payload = {
            "agentId": str(self.start_param.replace("ref_", "")),
            "resourceId": 2056
        }

        res = await http_client.post(
            "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/referral",
            json=payload
        )

        json = await res.json()

        if json['success']:
            result = await http_client.post(
                "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/participated",
                json=payload
            )

            json = await result.json()

            if json['success']:
                self.success(f"Successfully set up account!")

                login_task = {
                    "resourceId": 2057
                }

                complete = await self.complete_task(http_client=http_client, task=login_task)

                if complete == "done":
                    logger.success(f"Successfully checkin for the first time !")
        
        else:
            self.warning(f"Unknown error while trying to init account: {json}")

    async def get_user_info(self, http_client: aiohttp.ClientSession):
        try:
            payload = { "resourceId":2056 }

            result = await http_client.post(
                 f"https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/user/user-info",
                 json=payload,
            )

            json = await result.json()

            if json['code'] == '000000':
                data = json.get('data')
                if data['participated'] is False:
                    self.info('Attempt to set up account...')
                    await asyncio.sleep(delay=4)
                    await self.setup_account(http_client=http_client)
                    await asyncio.sleep(delay=3)
                    return await self.get_user_info(http_client=http_client)
                else:
                    meta_info = data.get('metaInfo')
                    total_grade = meta_info['totalGrade'] or 0
                    referral_total_grade = meta_info['referralTotalGrade'] or 0
                    total_balance = total_grade + referral_total_grade
                    current_attempts = (meta_info['totalAttempts'] or 0) - (meta_info['consumedAttempts'] or 0)
                    return meta_info, total_balance, current_attempts
        except Exception as e:
            self.error(f"Error occurred during getting user info: {e}")
            return None

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"<light-yellow>{self.session_name}</light-yellow> | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Proxy: {proxy} | 😢 Error: {error}")

    def update_headers(self, http_client: aiohttp.ClientSession):
        try:
            data = generate_random_data(headers['User-Agent'])
            payload = json.dumps(data)
            encoded_data = base64.b64encode(payload.encode()).decode()
            http_client.headers['Device-Info'] = encoded_data
            f_video_token = generate_f_video_token(196)
            http_client.headers['Fvideo-Id'] = secrets.token_hex(20)
            http_client.headers['Fvideo-Token'] = f_video_token
            http_client.headers['Bnc-Uuid'] = str(uuid.uuid4())
            http_client.headers['Cookie'] = f"theme=dark; bnc-uuid={http_client.headers['Bnc-Uuid']};"
        except Exception as error:
            logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Error occurred during updating headers {error}")

    async def get_task_list(self, http_client: aiohttp.ClientSession):
        payload = {
            "resourceId": 2056
        }

        response = await http_client.post(
            "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/list",
            json=payload
        )

        data = await response.json()

        if data['code'] == '000000':
            task_list = data['data']['data'][0]['taskList']['data']

            tasks = []

            for task in task_list:
                if task['type'] == "THIRD_PARTY_BIND":
                    continue
                elif task['status'] == "COMPLETED":
                    continue
                elif task['status'] == "IN_PROGRESS":
                    tasks.append(task)

            return tasks
        else:
            self.warning(f"Get tasks list failed: {data}")
            return None

    async def play_game(self, http_client: aiohttp.ClientSession):
        try:
            info = await self.get_user_info(http_client=http_client)

            if info['totalAttempts'] == info['consumedAttempts']:
                self.info(f"No Attempt left to play game...")
                return

            attempt_left = info['totalAttempts'] - info['consumedAttempts']
            self.info(f"Starting to play game...")

            while attempt_left > 0:
                self.info(f"Attempts left: <cyan>{attempt_left}</cyan>")

                payload = {
                    "resourceId": 2056
                }

                response = await http_client.post(
                    "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/start",
                    json=payload
                )

                game = await response.json()

                if game['success']:
                    self.success(f"Game <cyan>{data['data']['gameTag']}</cyan> started successful")

                    sleep = random.uniform(45, 45.05)

                    self.info(f"Wait {sleep}s to complete the game...")

                    await asyncio.sleep(delay=sleep)

                    check = await self.get_game_data(http_client=http_client, game=game)

                    if check:
                        await self.complete_game(http_client=http_client, game=game)
                        info = await self.get_user_info(http_client=http_client)
                        attempt_left = info['totalAttempts'] - info['consumedAttempts']

                else:
                    self.warning(f"Failed to start game, msg: {data}")
                    return

                sleep = random.uniform(5, 10)

                self.info(f"Sleep {sleep}s...")

                await asyncio.sleep(sleep_)
        except Exception as error:
            logger.error(f"Error occurred during play games {error}")

    async def run(self, proxy: str | None) -> None:
        if settings.USE_RANDOM_DELAY_IN_RUN:
            random_delay = random.randint(settings.RANDOM_DELAY_IN_RUN[0], settings.RANDOM_DELAY_IN_RUN[1])
            logger.info(f"<light-yellow>{self.session_name}</light-yellow> | Bot will start in <ly>{random_delay}s</ly>")
            await asyncio.sleep(random_delay)

        access_token = None
        refresh_token = None
        login_need = True

        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        http_client = CloudflareScraper(headers=headers, connector=proxy_conn)

        if proxy:
            await self.check_proxy(http_client=http_client, proxy=proxy)

        access_token_created_time = 0
        token_live_time = random.randint(28700, 28800)

        while True:
            try:
                if time() - access_token_created_time >= token_live_time:
                    login_need = True

                if login_need:
                    if "X-Growth-Token" in http_client.headers:
                        del http_client.headers["X-Growth-Token"]

                    tg_data = await self.get_tg_web_data(proxy=proxy)

                    self.update_headers(http_client=http_client)

                    access_token, refresh_token = await self.login(http_client=http_client, tg_data=tg_data)

                    http_client.headers['X-Growth-Token'] = f"{access_token}"

                    access_token_created_time = time()
                    token_live_time = random.randint(3500, 3600)

                    if self.first_run is not True:
                        self.success("Logged in successfully")
                        self.first_run = True

                    login_need = False

                await asyncio.sleep(delay=3)

            except Exception as error:
                logger.error(
                    f"<light-yellow>{self.session_name}</light-yellow> | 😢 Unknown error during login: {error}")
                await asyncio.sleep(delay=3)

            try:
                user, total_balance, current_attempts = await self.get_user_info(http_client=http_client)

                await asyncio.sleep(delay=2)

                if user is not None:
                    logger.info(f"<light-yellow>{self.session_name}</light-yellow> | Points: 💰<light-green>{'{:,}'.format(total_balance)}</light-green> 💰 | Your Attempts: 🚀<light-green>{'{:,}'.format(current_attempts)}</light-green> 🚀")

                    if settings.ENABLE_AUTO_TASKS:
                        tasks_list = await self.get_task_list(http_client=http_client)

                        if tasks_list is not None:
                            for task in tasks_list:
                                check = await self.complete_task(http_client=http_client, task=task)
                                if check == "done":
                                    self.success(f"Successfully completed task <cyan>{task['type']}</cyan> | Reward: <yellow>{task['rewardList'][0]['amount']}</yellow>")
                                else:
                                    self.warning(f"Failed to complete task: {task['type']}, msg: <light-yellow>{check}</light-yellow>")
                                await asyncio.sleep(random.uniform(3,5))

#                     if settings.ENABLE_AUTO_PLAY_GAMES:
#                         await self.play_games(http_client=http_client)

                sleep_in_seconds = random.choices([600, 1200, 1800, 2100], weights=[25, 25, 25, 25], k=1)[0]

                sleep_in_minutes = sleep_in_seconds / 60

                logger.info(f"<light-yellow>{self.session_name}</light-yellow> | 💤 sleep {sleep_in_minutes} minutes 💤")
                await asyncio.sleep(delay=sleep_in_seconds)

            except Exception as error:
                logger.error(
                    f"<light-yellow>{self.session_name}</light-yellow> | 😢 Unknown error: {error}")

async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | 😢 Invalid Session 😢")
