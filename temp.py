from utils import minecraft
import asyncio


if __name__ == "__main__":
    async def main():
        host = "minecraft.svat.dev"
        result = await minecraft.get_info_str(host)
        result_dict = await minecraft.get_info_dict(host)
        print(result, "\n\n", result_dict)

    asyncio.run(main())
