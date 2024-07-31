from aiocryptopay import AioCryptoPay, Networks
import tmp
import asyncio

crypto = AioCryptoPay(token='15699:AA3WCxN8t6sadGblvO9A57Yu9lXbwXeptHn', network=Networks.TEST_NET)


async def create(content: dict, chat_id: int):
    invoice = await crypto.create_invoice(asset='USDT', amount=content["price"],
                                          payload=str(chat_id) + " " + content["name"])
    print(str(chat_id) + " " + content["name"])
    return invoice.bot_invoice_url


async def on_pay():
    payload = "1150663089 Тест"
    print(1)
    await tmp.tmp(payload)
    print(2)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(on_pay())
