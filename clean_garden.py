import pathlib
p = pathlib.Path(__file__).with_name('garden.py')
s = p.read_text(encoding='utf-8')
# remove lines that are only backticks or start with backticks
lines = [ln for ln in s.splitlines() if not ln.strip().startswith('```')]
# also remove stray markdown fences that might appear as ````python
lines = [ln for ln in lines if not ln.strip().startswith('````')]
new = '\n'.join(lines) + '\n'
p.write_text(new, encoding='utf-8')
print('cleaned', p)
