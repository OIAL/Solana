swap = 0


                balances = trans_data.value.transaction.meta.post_token_balances

                for c in range(len(balances)):
                    balance = balances[c]
                    if str(balance.owner) == self.__AUTHORITY_ADDRESS and str(balance.mint) == self.__SOLANA_PUB_ADDRESS:
                        for c in range(len(trans_data.value.transaction.meta.pre_token_balances)):
                            pre_balance = trans_data.value.transaction.meta.pre_token_balances[c]
                            if str(pre_balance.owner) == self.__AUTHORITY_ADDRESS and str(
                                    pre_balance.mint) == self.__SOLANA_PUB_ADDRESS:
                                pre_amount = float(pre_balance.ui_token_amount.ui_amount_string)
                                break
                        swap = (float(balance.ui_token_amount.ui_amount_string) - pre_amount)

                        print(swap)
                        break