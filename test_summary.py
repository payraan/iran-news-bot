import asyncio

from services.summarizer import summarize_news


async def main():

    summary = await summarize_news(
        "Iran tensions rise after sanctions",
        "Western countries imposed new sanctions on Iran today..."
    )

    print(summary)


if __name__ == "__main__":
    asyncio.run(main())
