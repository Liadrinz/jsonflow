import re

def parse_template(template, kwargs, globals, locals):
    for match in re.findall(r'\<.*?\>', template):
        statement = match[1:-1]
        globals.update(kwargs)
        repl = eval(statement, globals, locals)
        template = template.replace(match, str(repl))
    return template
