![DetaMVC](https://detamvc.deta.dev/assets/images/detamvc.png)    


**Documentation:** [https://detamvc.deta.dev](https://detamvc.deta.dev)  
**Source Code:** [https://github.com/pyn-sol/detaMVC](https://github.com/pyn-sol/detaMVC)  


DetaMVC is a framework for rapidly developing and deploying web applications using:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Jinja2](https://fastapi.tiangolo.com/advanced/templates/?h=jinja2)
- [Deta](https://docs.deta.sh/docs/home)  


## Installation
```
pip install detamvc
```

Other Requirements:
- A Deta Account. If you do not have one, go to [Deta](https://www.deta.sh/) and click 'Join Deta'
- The [Deta CLI](https://docs.deta.sh/docs/cli/install)


## Basics
If you are familiar with Ruby on Rails, the commands are very similar for creating an application. 

```
detamvc new project

cd project

detamvc scaffold item name:str description:text price:float quantity:int available:bool
```

Before running your project, be sure to set your PROJECT_KEY for Deta. You can get this from your Deta dashboard under 'settings'.


```
echo DETA_PROJECT_KEY="#######_#############" > .env
```

Or, save yourself the hassle and set your development project key using the command. Hint: Do this _before_ creating a new project.

```
detamvc set-project-key #######_#################
```

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