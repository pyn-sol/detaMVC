from dataclasses import dataclass
from pathlib import Path
from os import walk, makedirs
from secrets import token_urlsafe
from detamvc.utilities import config


"""
HELPERS
"""


def __builder(
    project_path: str, 
    generator_path:str, 
    format_attrs: dict, 
    scaffold_obj_name=''
) -> None:
    """Build a project scaffold from a generator template.
    
    Args:
        project_path (str): The path to the directory where the project scaffold should be created.  
        generator_path (str): The path to the directory containing the generator template files.  
        format_attrs (dict): A dictionary of attributes to be used in formatting the generator template files.  
        scaffold_obj_name (str, optional): The name of the object being scaffolded. Defaults to an empty string.  
    """
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


def __format(doc: str, attr_dict: dict) -> str:
    """Format a document with the specified attribute dictionary.
    
    Args:
        doc (str): The document to be formatted.  
        attr_dict (dict): A dictionary of attributes to be used in the formatting.  
        
    Returns:
        str: The formatted string.
    """
    built_attrs = {}
    for k, v in attr_dict.items():
        if f'{{{k}}}' in doc:
            built_attrs.update({k: v})
    doc = doc.format(**built_attrs)
    return doc


def __get_object_attrs(attributes: list) -> dict:
    """Get a dictionary of object attributes from a list of attribute strings.
    
    Args:
        attributes (list): A list of strings representing object attributes in the form "name:type".  
        
    Returns:
        dict: A dictionary of object attributes, 
            where the keys are the attribute names and the values are the attribute types.
    """
    obj_attrs = dict()
    for a in attributes:
        if not a:
            continue
        s = a.split(':')
        obj_attrs[s[0]] = 'str' if len(s) == 1 else s[1].lower()
    return obj_attrs

def __prepare_model_attrs(obj_attrs: dict) -> str:
    """Provides attributes for the DetaModel  

    Args:
        obj_attrs (dict): attributes dictionary  

    Returns:
        str: prepared attributes as string
    """
    model_attrs = [
        f"{k}: {'str' if v in ('text', 'wysiwyg') else v}" 
        for k, v in obj_attrs.items()]
    return '\n    '.join(model_attrs)


def __create_form_attrs(attributes: dict, helpers_path: str) -> str:
    """Create form field HTML for the specified attributes.  
    
    Args:
        attributes (dict): A dictionary of form field attributes, 
            where the keys are the field names and the values are the field types.   
        helpers_path (str): The path to the directory containing form field helper templates.  
        
    Returns:
        str: The HTML for the form fields.
    """
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

def __add_wysiwyg_meta(take_action: bool):
    if take_action:
        with open(Path(__file__).parent.resolve() 
                  / 'templates/scaffold_helpers/trix_meta_content.html', 
                  'r') as o:
            return o.read()


def __get_import_placement(main_py: list) -> int:
    """Get the index at which to insert an import statement in the main Python script.  
    
    Args:
        main_py (list): A list of lines in the main Python script.  
        
    Returns:
        int: The index at which to insert an import statement.  
    """
    imp_placement = 0
    for i, line in enumerate(main_py):
        if '_router' in line and 'import' in line:
            imp_placement = i + 1
    return imp_placement


"""
GENERATORS
"""


def build_base(p: str, project_name: str, style: str) -> None:
    """Builds a base for the new project.  

    Currently supports two project bases: BOOTSTRAP and MKDOCS.  
    See templates/core/ or templates/mkdocs_core/ to see the files 
    which will be generated through the `__builder` method

    Args:
        p (str): the current working directory  
        project_name (str): name of the new project  
        style (str): style to build in.  
    """
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


def gen_scaffold(p: str, obj: str, attributes: list) -> None:
    """Generates Model, View, and Controller for a new Object.  

    Args:
        p (str): the current working directory  
        obj (str): the name of the new object to be created  
        attributes (list): the attributes of the new object
    """
    obj_attrs = __get_object_attrs(attributes)
    format_attrs = {
        'proj': Path.cwd().name,
        'obj': obj, 
        'Obj': obj.title(), 
        'model_attrs': __prepare_model_attrs(obj_attrs), 
        'form_attrs': __create_form_attrs(
            attributes=obj_attrs, 
            helpers_path='templates/scaffold_helpers'),
        'wysiwyg': __add_wysiwyg_meta('wysiwyg' in obj_attrs.values())}
    __builder(
        project_path=p, 
        generator_path='templates/scaffold', 
        format_attrs=format_attrs,
        scaffold_obj_name=obj)
    update(add_to_main(p, obj))

    

    with open(Path(__file__).parent.resolve() / 'templates/scaffold_helpers/scaffold_navlink.html', 'r') as o:
        scaffold_link = __format(o.read(), format_attrs)

    update(add_to_navlinks(
        p,
        content=scaffold_link))


def gen_authlib(p: str) -> None:
    """Generates a minimal authorization framework.

    Based on AuthLib library, the generate authorization framework
    allows users to login with Google. See AuthLib library for 
    other potential Open ID providers.  

    Args:
        p (str): the current working directory  
    """   
    obj = 'user'
    format_attrs = {
        'proj': Path.cwd().name,
        'obj': obj, 
        'Obj': obj.title() }

    __builder(
        project_path=p, 
        generator_path='templates/authlib_users', 
        format_attrs=format_attrs,
        scaffold_obj_name=obj)
    update(add_to_main(
        p, 
        obj, 
        extra_imports=[
            'from starlette.middleware.sessions import SessionMiddleware\n',
            'from os import environ\n'],
        extra_includes=[
            'app.add_middleware(SessionMiddleware, secret_key=environ.get("APP_SECRET"))\n']))
    update(add_to_requirements(
        p,
        reqs=['itsdangerous', 'httpx', 'Authlib', 'pyjwt', 'passlib[bcrypt]']))
    update(add_to_env(
        p,
        APP_SECRET='D' + token_urlsafe(16),
        GOOGLE_CLIENT_ID="",
        GOOGLE_CLIENT_SECRET=""))
    
    with open(Path(__file__).parent.resolve() / 'templates/scaffold_helpers/user_login.html', 'r') as o:
        user_links = o.read()

    update(add_to_navlinks(
        p,
        content=user_links))


"""
UPDATERS
"""
@dataclass 
class File:
    filepath: str 
    content: str
    mode: str = 'w'


def update(file: File):
    with open(file.filepath, file.mode) as m:
        m.write(file.content)

def add_to_main(
    p: str, 
    name: str,
    extra_imports: list or None = None, 
    extra_includes: list or None = None
) -> File:
    """Adds provided data to the main router with the scaffold router imports.  

    When a new scaffolded MVC is added to the project, the router for
    it should be added to main.py. This method will import the router 
    and include the router in the main `app`, along with the appropriate
    prefix. Extra imports and app additions may be appended as well.  

    Args:
        p (str): The path to the directory containing the main file.  
        name (str): name of the router to include.  
        extra_imports (listorNone, optional): additional imports to include. Defaults to None.  
        extra_includes (listorNone, optional): additional lines of code to include. Defaults to None.
    
    Return:
        File: the updated file and metadata
    """
    main_file = Path(p) / 'main.py'
    with open(main_file, 'r') as m:
        main = m.readlines()
    imprt = [f'from {name}.router import {name}_router\n']
    incld = [f'app.include_router({name}_router, tags=["{name}"], prefix="/{name}")\n']
    imprt += extra_imports or list()
    incld += extra_includes or list()
    main.insert(
        __get_import_placement(main), 
        ''.join(imprt))
    main.append(''.join(incld))
    return File(
        filepath=main_file, 
        content=''.join(main), 
        mode='w')


def add_to_requirements(p: str, reqs: list) -> File:
    """Adds provided data to the requirements file at the specified path with the provided requirements.  

    Args:
        p (str): The path to the directory containing the requirements file.  
        reqs (list): A list of requirements to be added to the requirements 
        
    Return:
        File: the updated file and metadata
    """
    req_file = Path(p) / 'requirements.txt'
    with open(req_file, 'r') as m:
        file_reqs = m.readlines()
    
    file_reqs.insert(0, '\n'.join(reqs) + '\n')
    return File(
        filepath=req_file, 
        content=''.join(file_reqs), 
        mode='w')


def add_to_env(p: str, **kwargs) -> File:
    """Adds provided data to the env file at the specified path with the provided variables.  

    Args:
        p (str): The path to the directory containing the env file.  
        kwargs: key and value for each entry 
        
    Return:
        File: the updated file and metadata
    """
    env_file = Path(p) / '.env'
    with open(env_file, 'r') as e:
        file_env = e.readlines()
    file_env += [
        f"{k}={v}"
        for k, v in kwargs.items()]
    return File(
        filepath=env_file, 
        content='\n'.join(file_env), 
        mode='w')


def add_to_navlinks(p: str, content: str):
    navlink_file = Path(p) / 'static_pages' / 'templates' / '_navlinks.html'
    with open(navlink_file, 'r') as e:
        file_navlink = e.read()
    return File(
        filepath=navlink_file,
        content=file_navlink + '\n\n' + content,
        mode='w')
