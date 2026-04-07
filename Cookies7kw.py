async def run_async_cpt_scrape(schedule):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel="chrome")
        
        # 1. Wczytujemy Twoje dane sesji
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # 2. Tworzymy kontekst (to jest Twoja "przeglądarka" z pamięcią)
        context = await browser.new_context()
        
        # 3. Formatujemy i dodajemy ciastka
        formatted_cookies = []
        for name, value in config['cookies'].items():
            formatted_cookies.append({
                'name': name,
                'value': value,
                'domain': '.zalan.do',  # Bardzo ważne: domena musi się zgadzać!
                'path': '/'
            })
        
        await context.add_cookies(formatted_cookies)
        
        # --- OD TERAZ KAŻDY PAGE W TYM CONTEXT JEST ZALOGOWANY ---
        
        tasks_list = []
        for item in schedule:
            # Przekazujemy ten sam zalogowany context do każdej tury
            tasks_list.append(scrape_single_wave(context, item['date'], item['time']))

        results = await asyncio.gather(*tasks_list)
        await browser.close()
        return results
