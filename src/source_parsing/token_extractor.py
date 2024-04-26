from abc import ABC, abstractmethod
import asyncio

from src.userbot.exceptions import TokenNotFoundInMessage


class AbstractTokenExtractor(ABC):
    @abstractmethod
    async def get_token_from_message(self, message_text: str) -> str:
        """
        Contains realization of token
        parsing from channel messages text.
        """
        raise NotImplementedError("Method get_token_from_message() not implemented.")


class FirstChannelTokenExtractor(AbstractTokenExtractor):
    """ МЕМ ЩИТКИ 🤖 NEW SOL POOLS (https://t.me/newsolanapairs) token extractor """
    async def get_token_from_message(self, message_text: str) -> str:
        if "token" in message_text.lower():
            parts = message_text.split("\n")
            return parts[3].replace("`", "")

        raise TokenNotFoundInMessage("Can't find token in message text from FIRST channel.")


class SecondChannelTokenExtractor(AbstractTokenExtractor):
    """ New Pairs — Trojan on Solana (https://t.me/NewPairsSolana) token extractor"""
    async def get_token_from_message(self, message_text: str) -> str:
        try:
            lines = message_text.split("\n")
            return lines[1].replace("`", "")
        except:
            raise TokenNotFoundInMessage("Can't find token in message text from SECOND channel.")


class ThirdChannelTokenExtractor(AbstractTokenExtractor):
    ...


class TestTokenExtractor(AbstractTokenExtractor):
    ...


if __name__ == "__main__":
    message = """RUTHSCHILD (https://solscan.io/token/jW5iGPqd51vqN8aYpzravdDSi4zqi3gssXTafrsxAHW)-SOL is on RAYDIUM (https://raydium.io/)

🏷 TOKEN
jW5iGPqd51vqN8aYpzravdDSi4zqi3gssXTafrsxAHW
Started: 26 seconds ago
Name: Jeeetcub Ruthschild
Price: $0.00000079
Market Cap: $791
Liquidity: $1.4K
Total supply: 1.0B

🛡️ SECURITY
Mutable metadata: NO
Mint authority: NO
Freeze authority: NO

👥 HOLDERS
10.00% - Deployer (https://solscan.io/account/65U1Nc4yfTwftYbmEKUcxkPuci1GybKTRVp4Qq4cPPTK)

🟥🟥 RATING  Risky
90.0% token supply was sent to other addresses by the deployer
10.0% token supply owned by the deployer
0.6 ratio of market cap to liquidity

📖 DESCRIPTION
i ohn yur moneh, i ohn yur women, i ohn yur weed, i ohn yur SOL. 
Website:https://jeetcubrotschild.com/ 
Twitter:https://twitter.com/ruthschildonsol 
Telegram:https://t.me/jeeetcubonsol

🔗 LINKS
Deployer (https://solscan.io/token/65U1Nc4yfTwftYbmEKUcxkPuci1GybKTRVp4Qq4cPPTK) | Image (https://bafybeiemiebo2m4yo7auf4abskwwwbsinellnasowihjpu7rg4x6dlzkgi.ipfs.nftstorage.link/)
BirdEye (https://birdeye.so/token/jW5iGPqd51vqN8aYpzravdDSi4zqi3gssXTafrsxAHW) | Raydium (https://raydium.io/swap/?inputCurrency=sol&outputCurrency=jW5iGPqd51vqN8aYpzravdDSi4zqi3gssXTafrsxAHW&inputAmount=0&fixed=in)
RugCheck (https://rugcheck.xyz/tokens/jW5iGPqd51vqN8aYpzravdDSi4zqi3gssXTafrsxAHW) | DexScreener (https://dexscreener.com/solana/jW5iGPqd51vqN8aYpzravdDSi4zqi3gssXTafrsxAHW) | Solscan (https://solscan.io/token/jW5iGPqd51vqN8aYpzravdDSi4zqi3gssXTafrsxAHW)

☀️ Maestro Bot - Revolutionize Your Solana Trading! (https://t.me/MaestroSniperBot?start=r-clckr)
    """
    first = FirstChannelTokenExtractor()
    token = asyncio.run(first.get_token_from_message(message))
    print(token)