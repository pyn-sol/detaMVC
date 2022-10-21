# DetaMVC


DetaMVC is a framework for rapidly developing web applications using:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Jinja2](https://fastapi.tiangolo.com/advanced/templates/?h=jinja2)
- [Deta](https://docs.deta.sh/docs/home)
- [ODetaM](https://github.com/rickh94/ODetaM)

## Work in Progress
Please note that DetaMVC is a work in progress currently. Some planned updates include:
- Support for exotic data types when scaffolding
- Implement Deta Auth when available
- Generate with other front ends ? (may take significant restructuring)

## Installation
```
pip install detamvc
```
   

## Basics
If you are familiar with Ruby on Rails, the commands are very similar for creating an application. 

```
detamvc new project

cd project

detamvc scaffold item name:str description:text price:float quantity:int available:bool
```

Before running your project, be sure to set your PROJECT_KEY for Deta. You can get this from your dashboard under 'settings'.


```
echo DETA_PROJECT_KEY="#######_#############" > .env
```

Or, save yourself the hassle and set your development project key using the command. Hint: Do this _before_ creating a new project.

```
detamvc set-project-key #######_#################
```

**NOTE**: Deta Base is used as your database. I would strongly recommend creating a new Project called 'development' where you can play around with ideas while building. When you go to production, create a new project in Deta for this to be managed in.

## Run a Server Manually

This assumes you have uvicorn installed. You can run with other servers as you wish - just set up like you would for a normal [FastAPI](https://fastapi.tiangolo.com/deployment/manually/ "Run a Server Manually - Uvicorn") application.
```
detamvc s
```
or
```
uvicorn main:app --reload
```

## Deploy on Deta
Now you can deploy this on Deta!
Before running the following, you will need to install the [Deta CLI](https://docs.deta.sh/docs/cli/install)
```
deta new --project default
```