from aiohttp import web
import ssl
from aiocryptopay import AioCryptoPay, Networks
from aiocryptopay.models.update import Update
import settings
import tmp

web_app = web.Application()
crypto = AioCryptoPay(token=settings.pay_token, network=Networks.TEST_NET)


@crypto.pay_handler()
async def invoice_paid(update: Update, app) -> None:
    print(update.payload)
    print(update.update_type)
    if update.update_type == "invoice_paid":
        await tmp.tmp(update.payload)


async def create(content: dict, chat_id: int):
    invoice = await crypto.create_invoice(asset='USDT', amount=content["price"],
                                          payload=str(chat_id) + " " + content["name"])
    print(str(chat_id) + " " + content["name"])
    return invoice.bot_invoice_url


async def close_session(app) -> None:
    await crypto.close()


ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('domain_srv.crt', 'domain_srv.key')
web_app.add_routes([web.post('/crypto-secret-path', crypto.get_updates)])
web_app.on_shutdown.append(close_session)
web.run_app(app=web_app, ssl_context=ssl_context)
