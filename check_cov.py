import json

data = json.load(open('coverage.json'))
files = []
for k, v in data['files'].items():
    percent = v['summary']['percent_covered']
    missing_lines = v['summary']['missing_lines']
    files.append({'file': k, 'percent': percent, 'missing': missing_lines})

files.sort(key=lambda x: x['percent'])
print("Lowest coverage files:")
for f in files[:30]:
    print(f"{f['file']}: {f['percent']:.2f}% (Missing lines: {f['missing']})")
