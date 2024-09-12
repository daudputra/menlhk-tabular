from src.controller.main_controller import MainController

import asyncio
import argparse

async def main(**kwargs):
    url = 'https://phl.menlhk.go.id/tabular'
    await MainController(url, **kwargs).main()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script untuk menjalankan dengan argumen.")
    parser.add_argument('--headless', action='store_true', help="Running Chromium dengan mode headless")
    parser.add_argument('--miniwin', action='store_true', help="mini windows")
    parser.add_argument('--s3', action='store_true', help="upload ke s3")

    args = parser.parse_args()
    kwargs = vars(args)
    asyncio.run(main(**kwargs))