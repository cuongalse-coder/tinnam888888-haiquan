from duckduckgo_search import DDGS
with DDGS() as ddgs:
    try:
        results = list(ddgs.text("thời tiết hôm nay", max_results=5))
        print(results)
    except Exception as e:
        print("ERROR:", e)
