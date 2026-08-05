import json
with open('experiments/reports/chunking_eval_results.json') as f:
    d = json.load(f)

queries = list(d['fixed'].keys())

for q in queries:
    print(f'\n==============================================')
    print(f'QUERY: {q}')
    print(f'==============================================')
    for strategy in ['fixed', 'structure', 'hybrid', 'small_to_big']:
        print(f'\n--- {strategy.upper()} ---')
        for i, res in enumerate(d[strategy][q][:2]):
            text = res['text'].replace('\n', ' ')
            if len(text) > 150:
                text = text[:150] + "..."
            print(f'  [{res["score"]:.3f}] {text}')
