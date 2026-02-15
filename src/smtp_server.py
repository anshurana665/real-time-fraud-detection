import asyncio
from aiosmtpd.controller import Controller

class CustomHandler:
    async def handle_DATA(self, server, session, envelope):
        print(f"\n📧 NEW EMAIL FROM: {envelope.mail_from}")
        print(f"TO: {envelope.rcpt_tos}")
        print("CONTENT:")
        print(envelope.content.decode('utf8', errors='replace'))
        print("--------------------------------------------------\n")
        return '250 Message accepted for delivery'

if __name__ == '__main__':
    controller = Controller(CustomHandler(), hostname='localhost', port=1025)
    controller.start()
    print("📧 SMTP Server running on localhost:1025...")
    print("Press Ctrl+C to stop.")
    try:
        # Keep the main thread alive
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_forever()
    except KeyboardInterrupt:
        print("\nStopping SMTP server...")
        controller.stop()
