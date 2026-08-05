import json
with open('experiments/reports/embedding_results.json') as f:
    d = json.load(f)
for q in d['small']['results']:
    print(f'\nQuery: {q}')
    for m in ['small', 'base']:
        print(f'  {m} ({d[m]["embed_time"]:.1f}s):')
        for i, res in enumerate(d[m]['results'][q][:3]):
            text_snippet = res['text'][:80].replace('\n', ' ')
            print(f'    {res["score"]:.3f} - {text_snippet}...')
