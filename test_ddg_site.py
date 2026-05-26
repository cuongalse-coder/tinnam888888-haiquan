from duckduckgo_search import DDGS
query = "Thông tư 121/2025/TT-BTC"
search_query = f'"{query}" site:thuvienphapluat.vn OR site:luatvietnam.vn OR site:chinhphu.vn OR site:haiquanonline.com.vn OR site:customs.gov.vn OR site:mof.gov.vn'
print("Query:", search_query)
with DDGS() as ddgs:
    results = list(ddgs.text(search_query, max_results=5))
    print("Results:", results)
