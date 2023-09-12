from flask import Flask, render_template, request, redirect, session, url_for
from sqlalchemy import create_engine, Column, String, Integer, asc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
Base = declarative_base()

#Create db model
class Jugadores(Base):
    __tablename__ = "Jugadores"
    id = Column("Id",Integer, primary_key=True)
    name = Column("Name", String(200), nullable = False)
    doble9 = Column("doble9",Integer)
    doble8 = Column("doble8",Integer)
    doble7 = Column("Doble7",Integer)
    doble6 = Column("Doble6",Integer)
    doble5 = Column("Doble5",Integer)
    doble4 = Column("Doble4",Integer)
    doble3 = Column("Doble3",Integer)
    doble2 = Column("Doble2",Integer)
    doble1 = Column("Doble1",Integer)
    doble0 = Column("Doble0",Integer)
    total = Column("Total", Integer)

    def __init__(self, id, name, doble9=0, doble8=0, doble7=0, doble6=0, doble5=0, doble4=0, doble3=0, doble2=0, doble1=0, doble0=0,total=0):
        self.id = id
        self.name = name
        self.doble9 = doble9
        self.doble8 = doble8
        self.doble7 = doble7
        self.doble6 = doble6
        self.doble5 = doble5
        self.doble4 = doble4
        self.doble3 = doble3
        self.doble2 = doble2
        self.doble1 = doble1
        self.doble0 = doble0
        self.total = total
    
    #Create a function to return a string when we add something
    def __repr__(self):
        return f"{self.name},{self.doble9},{self.doble8},{self.doble7},{self.doble6},{self.doble5},{self.doble4},{self.doble3},{self.doble2},{self.doble1},{self.doble0}"

class Game_stage(Base):
    __tablename__ = "Game_stage"
    id = Column("Id", Integer, primary_key=True)
    stage = Column("Game stage", String(20), nullable= False)

    def __init__(self,stage="Inicio"):
        self.stage = stage

    def __repr__(self):
        return f"Estas en el stage: {self.stage}"
    
class Qty(Base):
    __tablename__ = "Qty"
    id = Column('Id', Integer, primary_key=True)
    qty = Column("Qty", Integer)

    def __init__(self,qty):
        self.qty = qty


engine = create_engine("sqlite:///jugadores.db", echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()



@app.route('/',methods = ['POST', 'GET'])
def initial():
    if request.method == 'GET':
        session.query(Jugadores).delete()
        session.query(Game_stage).delete()
        session.query(Qty).delete()
        session.commit()
        return render_template('initial.html')
    elif request.method =='POST':
        qty = request.form.get("qty")
        session.add(Qty(qty))
        session.commit()
        return redirect(url_for('index'))
        

@app.route('/index', methods = ['POST', 'GET'])
def index():
    if request.method =="GET":
        session.add(Game_stage())
        session.commit()
        game_stage = session.query(Game_stage.stage).all()
        game_stage = game_stage[0][0]
        qty = session.query(Qty.qty).all()[0][0]
        return render_template(
            'index.html',game_stage=game_stage, qty=qty)
    elif request.method == "POST":
        jugadores = request.form.getlist("jugadores")
        i = 0
        for jugador in jugadores:
            i +=1
            session.add(Jugadores(i,jugador))
        return redirect(url_for('gameindex'))
    

@app.route('/gameindex', methods=['GET','POST'])
def gameindex():
    if request.method == 'GET':
        jugadores = session.query(Jugadores).all()
        session.query(Game_stage).filter(Game_stage.id == 1).update({'stage':"doble9"})
        session.commit()
        game_stage = session.query(Game_stage.stage).all()[0][0]
        return render_template("gameindex.html",jugadores=jugadores, game_stage=game_stage)
    elif request.method == 'POST':
        jugadores = session.query(Jugadores).all()
        points = request.form.getlist("points")
        game_stage = session.query(Game_stage.stage).all()[0][0]
        i = 0
        for point in points:
            i +=1
            session.query(Jugadores).filter(Jugadores.id == i).update({f'{game_stage}': point})
        game_stage = str(game_stage)
        game_num = int(game_stage[-1])-1
        game_stage = game_stage[:-1]+str(game_num)
        session.query(Game_stage).filter(Game_stage.id == 1).update({'stage':f"{game_stage}"})
        session.commit()        
        game_stage = session.query(Game_stage.stage).all()[0][0]
        if game_stage != "doble-1":
            return render_template('gameindex.html',jugadores=jugadores,game_stage=game_stage)
        else:
            return redirect(url_for('winner'))
        
@app.route('/winner', methods = ['GET', 'POST'])
def winner():
    if request.method == 'GET':
        jugadores = session.query(Jugadores).all()
        for jugador in jugadores:
            jugador.total=jugador.doble9 + jugador.doble8 + jugador.doble7 +jugador.doble6 +jugador.doble5 +jugador.doble4+jugador.doble3+jugador.doble2+jugador.doble1+jugador.doble0
        session.query(Game_stage).filter(Game_stage.id == 1).update({'stage':"Ganador"})
        session.commit()
        game_stage = session.query(Game_stage.stage).all()[0][0]
        jugadores = session.query(Jugadores).order_by(Jugadores.total.asc()).all()
        session.commit()
        ganador = jugadores[0].name
        return render_template('winner.html',jugadores=jugadores,game_stage=game_stage,ganador=ganador)
    elif request.method =='POST':
        return redirect(url_for('initial'))





if __name__ == "__main__":
    app.run(host='localhost', port=4000, debug=True)