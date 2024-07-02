# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         a 
# Author:       yepeng
# Date:         2021/10/22 2:44 下午
# Description: 
# -------------------------------------------------------------------------------
# jup-swap/api.py
import json
from dataclasses import dataclass, asdict
from typing import Optional, Any, List

import requests


@dataclass
class Result:
    """
    Represents the result of an operation.

    Attributes:
        is_ok (bool): Indicates whether the operation was successful.
        data (Any): The data returned on success.
        err_code (Optional[str]): Error code returned on failure.
        err_msg (Optional[str]): Error message returned on failure.
    """
    is_ok: bool
    data: Any
    err_code: Optional[str] = None
    err_msg: Optional[str] = None

    def data_json(self) -> str:
        """
                Returns a JSON formatted string representation of the Result object.
                """
        return json.dumps(asdict(self), indent=4)

    @staticmethod
    def from_ok(data):
        """
        Creates a Result instance for a successful operation.

        Args:
            data (Any): The data returned on success.

        Returns:
            Result: A Result instance indicating success with the provided data.
        """
        return Result(is_ok=True, data=data)

    @staticmethod
    def from_err(code, msg):
        """
        Creates a Result instance for a failed operation.

        Args:
            code (str): The error code returned on failure.
            msg (str): The error message returned on failure.

        Returns:
            Result: A Result instance indicating failure with the error code and message.
        """
        return Result(is_ok=False, data=None, err_code=code, err_msg=msg)


class JupApiClient:
    """
    Client for interacting with Jup API.

    Attributes:
        base_url (str): The base URL of the Jup API.
    """

    def __init__(self, base_url: str = "https://quote-api.jup.ag/v6"):
        """
        Initializes the JupApiClient with the base URL.

        Args:
            base_url (str): The base URL of the Jup API.default "https://quote-api.jup.ag/v6"
        """
        self.base_url = base_url

    def quote(self, inputMint: str, outputMint: str,
              amount: int,
              slippageBps: Optional[int] = None,
              exactIn: bool = True,
              platformFeeBps: Optional[int] = None,
              onlyDirectRoutes: Optional[bool] = None,
              asLegacyTransaction: Optional[bool] = None,
              excludeDexes: Optional[list] = None,
              maxAccounts: Optional[int] = None) -> Result:
        """
        Performs a quote request to the Jup API.

        Args:
            inputMint (str): The input token mint address.
            outputMint (str): The output token mint address.
            amount (int): The amount of input tokens.
            slippageBps (Optional[int]): BPS slippage percentage.
            exactIn (bool): Swap mode (ExactIn or ExactOut).
            platformFeeBps (Optional[int]): Platform fee in BPS.
            onlyDirectRoutes (Optional[bool]): Whether to limit to direct routes.
            asLegacyTransaction (Optional[bool]): Whether to use legacy transaction.
            excludeDexes (Optional[list]): List of DEXes to exclude.
            maxAccounts (Optional[int]): Maximum number of accounts involved in routing.

        Returns:
            Result: A Result object with quote response data or error details.
                The data returned on success will be a dictionary with keys:
                - inputMint: Input token mint address.
                - inAmount: Amount of input tokens.
                - outputMint: Output token mint address.
                - outAmount: Amount of output tokens.
                - otherAmountThreshold: Threshold amount for other tokens.
                - swapMode: Swap mode used (ExactIn or ExactOut).
                - slippageBps: BPS slippage percentage.
                - platformFee: Platform fee information.
                - priceImpactPct: Price impact percentage.
                - routePlan: List of route plans with swap information.
                - contextSlot: Context slot information.
                - timeTaken: Time taken for the operation.
                Example:
                {
                    'inputMint': 'So11111111111111111111111111111111111111112',
                    'inAmount': '1000000',
                    'outputMint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
                    'outAmount': '148206',
                    'otherAmountThreshold': '148192',
                    'swapMode': 'ExactIn',
                    'slippageBps': 1,
                    'platformFee': None,
                    'priceImpactPct': '0',
                    'routePlan': [
                        {
                            'swapInfo': {
                                'ammKey': 'DJFoQN5yNVtoEhoXiKqmYFXowQcPJSvB3BAavEcdEi7s',
                                'label': 'Meteora DLMM',
                                'inputMint': 'So11111111111111111111111111111111111111112',
                                'outputMint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
                                'inAmount': '1000000',
                                'outAmount': '148206',
                                'feeAmount': '104',
                                'feeMint': 'So11111111111111111111111111111111111111112'
                            },
                            'percent': 100
                        }
                    ],
                    'contextSlot': 275023015,
                    'timeTaken': 0.031721628
                }
        """
        url = self.base_url + "/quote"
        params = {
            "inputMint": inputMint,
            "outputMint": outputMint,
            "amount": amount,
            "slippageBps": slippageBps,
            "swapMode": "ExactIn" if exactIn else "ExactOut",
            "platformFeeBps": platformFeeBps,
            "onlyDirectRoutes": onlyDirectRoutes,
            "asLegacyTransaction": asLegacyTransaction,
            "excludeDexes": excludeDexes,
            "maxAccounts": maxAccounts
        }
        response = requests.get(url, params=params)

        return self._handle_response(response)

    def swap(self, userPublicKey: str,
             quoteResponse: dict,
             wrapAndUnwrapSol: Optional[bool] = True,
             useSharedAccounts: Optional[bool] = True,
             feeAccount: Optional[str] = None,
             computeUnitPriceMicroLamports: Optional[int] = None,
             asLegacyTransaction: Optional[bool] = False,
             useTokenLedger: Optional[bool] = False,
             destinationTokenAccount: Optional[str] = None) -> Result:
        """
                Perform a swap operation using the Jupiter API.

                Args:
                    userPublicKey (str): User's public key.
                    quoteResponse (dict): Response object obtained from a quote API call.
                    wrapAndUnwrapSol (bool, optional): Flag to automatically wrap/unwrap SOL. Defaults to True.
                    useSharedAccounts (bool, optional): Flag to use shared program accounts. Defaults to None.
                    feeAccount (str, optional): Fee token account for output tokens. Defaults to None.
                    computeUnitPriceMicroLamports (int, optional): Price per computation unit in micro lamports. Defaults to None.
                    asLegacyTransaction (bool, optional): Flag to request a legacy transaction. Defaults to None.
                    useTokenLedger (bool, optional): Flag to use token ledger for transfer of input token amounts. Defaults to None.
                    destinationTokenAccount (str, optional): Public key of the token account to receive tokens from the swap. Defaults to None.

                Returns:
                    Result: Result object containing either swap transaction data or error information.
                        - If successful, is_ok is True and data contains:
                          {
                              'swapTransaction': '<base64 encoded transaction data>',
                              'lastValidBlockHeight': <int>,
                              'prioritizationFeeLamports': <int>
                          }
                        - If there's an error, is_ok is False and err_code/err_msg contain error details.
                """
        url = self.base_url + "/swap"
        params = {
            "userPublicKey": userPublicKey,
            "quoteResponse": quoteResponse,
            "wrapAndUnwrapSol": wrapAndUnwrapSol,
            "useSharedAccounts": useSharedAccounts,
            "feeAccount": feeAccount,
            "computeUnitPriceMicroLamports": computeUnitPriceMicroLamports,
            "asLegacyTransaction": asLegacyTransaction,
            "useTokenLedger": useTokenLedger,
            "destinationTokenAccount": destinationTokenAccount
        }
        response = requests.post(url, json=params)

        return self._handle_response(response)

    @staticmethod
    def _handle_response(response) -> Result:
        try:
            if response.status_code == 200:
                res = response.json()
                return Result.from_ok(data=res)
            else:
                res = response.json()
                return Result.from_err(res['errorCode'], res['error'])
        except Exception as e:
            return Result.from_err("SYSTEM_ERROR", str(e))

    def price(self, ids: List[str], vsToken: str = "USDC") -> Result:
        # https://price.jup.ag/v6/price?ids=SOL
        url = "https://price.jup.ag/v6/price"
        print(url)
        ids = ','.join(ids)
        print(ids)
        params = {
            "ids": ids,
            "vsToken": vsToken
        }
        response = requests.get(url, params=params)
        return self._handle_response(response)

    def comb_swap(self, userPublicKey: str, inputMint: str, outputMint: str,
                  amount: int,
                  slippageBps: Optional[int] = None,
                  exactIn: bool = True) -> Result:
        quote_result = self.quote(inputMint=inputMint, outputMint=outputMint, amount=amount, exactIn=exactIn,
                                  slippageBps=slippageBps)
        if not quote_result.is_ok:
            return quote_result

        quote_resp = quote_result.data
        swap_result = self.swap(userPublicKey=userPublicKey, quoteResponse=quote_resp)
        return swap_result
