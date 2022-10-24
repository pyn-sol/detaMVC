from pathlib import Path
from os import walk, makedirs
from .utilities import config


def __builder(project_path, generator_path, format_attrs: dict, scaffold_obj_name=''):
    project_path = Path(project_path)
    generator_path = Path(__file__).parent.resolve() / generator_path
    for (dirpath, _, filenames) in walk(generator_path):
        np = (Path(scaffold_obj_name) / project_path 
              if scaffold_obj_name else project_path)
        new_path = dirpath.replace(str(generator_path), str(np))
        if '__pycache__' in str(dirpath):
            continue
        makedirs(new_path, exist_ok=True)
        for filename in filenames:
            full_path = Path(dirpath) / filename
            print(f">> {Path(new_path) / filename}")
            with open(full_path, 'r') as c:
                content = c.read()          
            
            with open(Path(new_path) / filename, 'w+') as o:
                o.write(__format(content, format_attrs))


def build_base(p, project_name, style):
    makedirs(p)
    content_attrs = {
        'Obj': project_name.title(),
        'project_key': config('project_key') or ''}

    gen_path = 'core'
    if style == 'MKDOCS':
        gen_path = 'mkdocs_core'

    __builder(
        project_path=p, 
        generator_path=f'templates/{gen_path}', 
        format_attrs=content_attrs)


def gen_scaffold(p, obj, attributes):
    obj_attrs = __get_object_attrs(attributes)
    model_attrs = '\n    '.join([f"{k}: {'str' if v == 'text' else v}" for k, v in obj_attrs.items()])
    form_attrs = __create_form_attrs(
        attributes=obj_attrs, 
        helpers_path='templates/scaffold_helpers')
    format_attrs = {
        'proj': Path.cwd().name,
        'obj': obj, 
        'Obj': obj.title(), 
        'model_attrs': model_attrs, 
        'form_attrs': form_attrs}
    __builder(
        project_path=p, 
        generator_path='templates/scaffold', 
        format_attrs=format_attrs,
        scaffold_obj_name=obj)

    update_main(p, obj)


def update_main(p, name):
    main_file = Path(p) / 'main.py'
    with open(main_file, 'r') as m:
        main = m.readlines()
    imp = f'from {name}.router import {name}_router\n'
    inc = f'app.include_router({name}_router, tags=["{name}"], prefix="/{name}")\n'
    imp_placement = 0
    for i, line in enumerate(main):
        if '_router' in line and 'import' in line:
            imp_placement = i + 1
    main.insert(imp_placement, imp)
    main.append(inc)

    with open(main_file, 'w') as m:
        m.write(''.join(main))


def __format(doc, attr_dict):
    built_attrs = {}
    for k, v in attr_dict.items():
        if f'{{{k}}}' in doc:
            built_attrs.update({k: v})
    if built_attrs:
        doc = doc.format(**built_attrs)
    return doc


def __get_object_attrs(attributes):
    obj_attrs = dict()
    for a in attributes:
        if not a:
            continue
        s = a.split(':')
        obj_attrs[s[0]] = 'str' if len(s) == 1 else s[1].lower()
    return obj_attrs

def __create_form_attrs(attributes, helpers_path):
    helpers_path = Path(__file__).parent.resolve() / helpers_path
    form_fields = list()
    for f, t in attributes.items():
        field_helper = helpers_path / f'{t}.html'
        if not field_helper.exists():
            field_helper = helpers_path / 'str.html'
        with open(field_helper, 'r') as o:
            content = o.read()
        format_attrs = {'f': f, 'F': f.title()}
        form_fields.append(__format(content, format_attrs))
    return '\n'.join(form_fields)
