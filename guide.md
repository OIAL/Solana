- Как отслеживать транзакции по контракту?
  - Необходимо подписаться на логи Solana. 
  Для этого импортируем объект коннекта и вебсокета из офф.
  библиотеки Solana `from solana.rpc.websocket_api import connect, SolanaWsClientProtocol`
  Так же необходима RPC которая поддерживает подписку на метод `logsSubscribe` (Helius, Ankor).
  Создаем функцию
  ```
  RAYDIUM_LIQUIDITY = '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8'
       while True:
            start_time = time.time()
            async with connect(wss_url_helius) as solana_websocket:
                solana_websocket: SolanaWsClientProtocol
                address = Pubkey.from_string(RAYDIUM_LIQUIDITY)
                commitment = Commitment('processed')
                await solana_websocket.logs_subscribe(
                    filter_=RpcTransactionLogsFilterMentions(lp_adress),
                    commitment=commitment)
                # processed → confirmed → finalized
                solana_websocket.close_timeout = 0
                a = await solana_websocket.recv()
                signature_cache = []
                while True:
                    last_call = time.time()
                    msg = await solana_websocket.recv()
                    result = msg[0].result
                    error_status = result.value.err
                    if error_status is None:
                        logs = result.value.logs
                        signature = result.value.signature
   ```
  - Таким методом мы будем получать все валидные транзакции по адрессу LP на Raydium, следующим шагом мы по `Signature` 
    получим данные о транзакции. Для следующего шага нам нужно знать `TokenContractAdress`
    ```
    client = AsyncClient(rpc_url_helius, commitment=Commitment("confirmed"))
    trans_data = await client.get_transaction(tx_sig=signature,
                                                           max_supported_transaction_version=0,
                                                           commitment=Commitment('confirmed'))
    ```
  - Необходимо получить текущую цену токена. Вычисляем ее из `post_token_balances`.
    ```			
            if trans_data.value is not None:
                try:
                    a_value = trans_data.value
                    trans_info = a_value.transaction
                    meta_data = trans_info.meta
                    post_balances = meta_data.post_token_balances
                    instructions = trans_data.value.transaction.transaction.message.instructions
                    logs = trans_data.value.transaction.meta.log_messages
                    accounts = trans_data.value.transaction.transaction.message.account_keys
                    for balance in post_balances:
                        if str(balance.owner) == authority_address and str(
                                balance.mint) != solana_pub_address:
                            token_pub_address = balance.mint
                            lp_token_amount = int(balance.ui_token_amount.amount)
                            token_decimals = balance.ui_token_amount.decimals
                        if str(balance.mint) == solana_pub_address and str(balance.owner) == authority_address:
                            lp_solana_amount = int(balance.ui_token_amount.amount)
                            solana_decimals = balance.ui_token_amount.decimals
                        if int(lp_token_amount) != 0 and int(lp_solana_amount) != 0:
                            token_price_in_solana = lp_solana_amount / lp_token_amount
    ```
    Объем свапа можно вычислить путем сравнения `pre_token_balances` и `post_token_balances` 
  где `balance.owner == owner.pubkey()`, таким образом получим объем в SOL и в токенах.

- Получаем такой роут: Проверка `.json` на контракты, сравниваем с `dict()` в кеше, запускаем вебсокеты по каждому `LP_adress`, 
  добавляем в функцию `start_time` чтобы отслеживать длительность парсинга, по каждой транзакции получаем данные через `get_transaction`, получаем цену и объем
    
- Пример `.json`: 
  ``` 
  "lp_adress": "token_adress"
  ```
- Нужно выбрать, использовать файл `.json` или DB по типу `postgres`, использовать их вместе нет никакого смысла.
  Коргда приходит время удалять контракт с мониторинга: a) Удаляем его из `.json`, b) Удаляем запись из DB, делаем `break` 
  в самом вебсокете
- Количество токенов, которые возможно одновременно отслеживать напрямую зависит от пропускной способности RPC, т.к.
  получение данных об 1 транзакции = 1 RPC_call. Так же в расчет нужно учитывать волатильности каждого токена, т.е. 
  чем более волатильная цена, тем болоше транзакций в секунду необходимо расшифровывать с блокчейна. 
- Так же нужна иметь в виду что 1 вебсокет может использовать до 7-10GB данных в день (120КБ/сек)
- Необходимо использовать ассинхронность иначе все запросы будут линейными.
- Документация по `Solana` - https://michaelhly.com/solana-py/