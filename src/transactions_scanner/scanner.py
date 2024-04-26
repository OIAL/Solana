import os
import sys
from datetime import datetime
import asyncio

from loguru import logger

from dotenv import load_dotenv

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solana.rpc.websocket_api import connect, SolanaWsClientProtocol
from solana.exceptions import SolanaRpcException
from solders.pubkey import Pubkey
from solders.rpc.config import RpcTransactionLogsFilterMentions
from solders.signature import Signature
from websockets.exceptions import ConnectionClosedError

sys.path.append("../")

import requests


load_dotenv()


BOT_API: str = os.getenv("BOT_API")
OUTPUT_CHAT_ID: int = int(os.getenv("OUTPUT_CHAT_ID"))
HELIUS_API_KEY: str = os.getenv("HELIUS_API_KEY")
INCLUDE_ERROR_TX: bool = bool(int(os.getenv("INCLUDE_ERROR_TX")))
# SOLANA_TOKENS_IGNORE_RANGE in .env example: "-10;-5"
SOLANA_TOKENS_IGNORE_RANGE: list[float] = sorted([
    float(os.getenv("SOLANA_TOKENS_IGNORE_RANGE").split(";")[0]),
    float(os.getenv("SOLANA_TOKENS_IGNORE_RANGE").split(";")[1])
])


async def send_transaction(*, token: str, signature: str, swap: float):
    text = f"Token: {token}"
    r = requests.get(f"https://api.telegram.org/bot{BOT_API}/sendMessage?chat_id={OUTPUT_CHAT_ID}&text={text}")


class TransactionsScanner:
    def __init__(self):
        # Constants.
        self.__SOLANA_PUB_ADDRESS = "So11111111111111111111111111111111111111112"
        self.__AUTHORITY_ADDRESS = "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"
        self.__RAYDIUM_LIQUIDITY = "MZz5KkdUoxfc8ZgfM1PdxqjA3YpaDa6Knwm5xGNkoLK"
        self.__WSS_URL_HELIUS = f"wss://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
        self.__RPC_URL_HELIUS = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

        # Solana connections.
        self.solana_websocket = connect(self.__WSS_URL_HELIUS)
        self.client = AsyncClient(self.__RPC_URL_HELIUS, commitment=Commitment("finalized"))

    async def get_swap(self, trans_data) -> float:
        swap = 0

        balances = trans_data.value.transaction.meta.post_token_balances

        for c in range(len(balances)):
            balance = balances[c]
            if (str(balance.owner) == self.__AUTHORITY_ADDRESS
                    and str(balance.mint) == self.__SOLANA_PUB_ADDRESS):
                for c in range(len(trans_data.value.transaction.meta.pre_token_balances)):
                    pre_balance = trans_data.value.transaction.meta.pre_token_balances[c]
                    if str(pre_balance.owner) == self.__AUTHORITY_ADDRESS and str(
                            pre_balance.mint) == self.__SOLANA_PUB_ADDRESS:
                        pre_amount = float(pre_balance.ui_token_amount.ui_amount_string)
                        break
                swap = (float(balance.ui_token_amount.ui_amount_string) - pre_amount)
                break

        return swap

    async def send_tx(self, signature, token):
        try:
            trans_data = await self.client.get_transaction(
                tx_sig=signature,
                max_supported_transaction_version=0,
                commitment=Commitment('finalized')
            )
        except SolanaRpcException:
            await asyncio.sleep(5)
            return 0

        if trans_data.value is not None:
            try:

                swap = await self.get_swap(trans_data)

                if SOLANA_TOKENS_IGNORE_RANGE[0] <= swap <= SOLANA_TOKENS_IGNORE_RANGE[1]:
                    logger.warning(
                        f"Transaction not satisfying the conditions, shouldn't be in range {SOLANA_TOKENS_IGNORE_RANGE[0]};{SOLANA_TOKENS_IGNORE_RANGE[1]}")
                    logger.info(f"Signature: {str(signature)}")
                    logger.info(f"SWAP: {swap}")
                    return 1
                else:
                    await send_transaction(token=token, signature=str(signature), swap=swap)
                    logger.success("Transaction satisfying the conditions.")
                    logger.info(f"Signature: {str(signature)}")
                    logger.info(f"SWAP: {swap}")
                    return 2

            except Exception as e:
                logger.warning(f"Error in get tx info! '{e}'")
                return 0

    async def get_transaction_block(self, signature, token, result):
        error_status = result.value.err

        if error_status:
            # print(f"{result=}")
            # print(f"{error_status=}")
            if not INCLUDE_ERROR_TX:
                # logger.info("Error in tx, skip")
                return
            else:
                logger.info("Error in tx.")

        counter = 0
        while counter <= 10:
            exit_code = await self.send_tx(signature, token)
            counter += 1
            if exit_code == 0:
                await asyncio.sleep(1)
                continue
            else:
                break

    async def scan_transactions(self, token: str, scanning_minutes: int) -> None:
        """
        Scans solana signatures, recieved from
        websocket.
        """
        scanning_start_time = datetime.utcnow()
        logger.info(f"Signatures scanning initiated, {token=}")
        logger.info(f"Scanning start time is: {scanning_start_time.strftime('%H:%M:%S')}")

        # with open(f"{token}.txt", "w") as file:  # Creating file, that conatains token's signatures.
        #     print("File created")

        async with self.solana_websocket as conn:
            conn: SolanaWsClientProtocol
            address = Pubkey.from_string(token)
            commitment = Commitment('finalized')
            await conn.logs_subscribe(
                filter_=RpcTransactionLogsFilterMentions(address),
                commitment=commitment)
            conn.close_timeout = 0
            a = await conn.recv()
            signature_cache = []
            while True:
                last_call_time = datetime.utcnow()
                time_delta = last_call_time - scanning_start_time
                if time_delta.seconds >= scanning_minutes * 60:
                    logger.info(f"Last call time is: {last_call_time.strftime('%H:%M:%S')}")
                    logger.success(f"Time limit reached for {token}."
                                   f" Scanning end time is: {datetime.utcnow().strftime('%H:%M:%S')}")
                    await self.kill_websocket()
                    return

                try:
                    msg = await conn.recv()
                    result = msg[0].result

                    logs = result.value.logs

                    signature = result.value.signature
                    # logger.info(f"Handle tx {signature}")

                    # with open(f"{token}.txt", "a") as file:
                    #     file.write(f"{signature}\n")

                    asyncio.ensure_future(self.get_transaction_block(signature, token, result))

                except Exception as e:
                    logger.warning(f"Handle error '{str(e)}', restart!")
                    await asyncio.sleep(1)

    async def kill_websocket(self) -> None:
        """
        Closes client,
        refuseses connection with
        websocket.
        """
        # logger.info(f"Scanning end time is: {datetime.utcnow().strftime('%H:%M:%S')}")

        await self.client.close()
        logger.success("Client was successfuly closed.")
        async with self.solana_websocket as conn:
            await conn.close()

        logger.success("Connection with solana websocket was successfuly refused.")


if __name__ == '__main__':
    token_arg = sys.argv[1]
    scanning_minutes_arg = int(sys.argv[2])  # Minutes.
    scanner = TransactionsScanner()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scanner.send_tx(signature=Signature.from_string(
        "L6LK14mRW66Mjgx38rRExmBpdbfVUG9MCuBc5UB1FjFCAxKhvWYQQK7gtQX4oVsfZVn1oDb1876uVjnj8oxswy7"),
        token="HN3Gh5Yx9u7KNy64yrraQiBUFvKRhr1Uhvgify7bnRTp"
    ))
    loop.run_until_complete(scanner.scan_transactions(token_arg, scanning_minutes_arg))
