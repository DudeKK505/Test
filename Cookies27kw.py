async def run_async_cpt_scrape(schedule):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel="chrome")
        
        # 1. Wczytaj swój config.json
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # 2. Tworzymy kontekst z Twoimi nagłówkami (bez ciastek)
        # Wyciągamy ciastka z nagłówków, jeśli tam są, bo Playwright woli je osobno
        clean_headers = {k: v for k, v in config['headers'].items() if k.lower() != 'cookie'}

        context = await browser.new_context(
            extra_http_headers=clean_headers,
            user_agent=config['headers'].get('user-agent', '') # Opcjonalnie wyciągnij UA
        )

        # 3. Wstrzykujemy ciasteczka
        # Playwright wymaga listy słowników z polami name, value i domain
        formatted_cookies = []
        for name, value in config['cookies'].items():
            formatted_cookies.append({
                'name': name,
                'value': value,
                'domain': 'zalos-lodz-frontend-live.logistics.zalan.do', # Musi pasować do domeny WMS
                'path': '/'
            })
        
        await context.add_cookies(formatted_cookies)

        # Teraz każda nowa strona w tym kontekście ma Twoją sesję
        tasks_list = [scrape_single_wave(context, item['date'], item['time']) for item in schedule]
        results = await asyncio.gather(*tasks_list)
        
        await browser.close()
        return results
