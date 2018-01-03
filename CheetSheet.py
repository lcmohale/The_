import flask
from flask_pymongo import PyMongo
from flask import Flask, render_template, url_for, request, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
mongo = PyMongo(app)

class Person(object):
    def __init__(self,gender, name, surname, date_of_birth, cell_no, Email, occupation, place_of_birth, current_place):
        self.id = id
        self.gender = gender
        self.name = name
        self.surname = surname
        self.date_of_birth = date_of_birth
        self.cell_no = cell_no
        self.Email = Email
        self.occupation = occupation
        self.place_of_birth = place_of_birth
        self.current_place = current_place
        self.relations = []
    
    def _json(self):
        json = {'gender':self.gender,
				'name':self.name,
				'surname':self.surname,
				'date_of_birth':self.date_of_birth,
				'cell_no':self.cell_no,
				'Email':self.Email,
				'occupation':self.occupation,
				'place_of_birth':self.place_of_birth,
				'current_place':self.current_place,
				'relations':self.relations
				}
				 
        return json 
				 
				 
class Relation(object):
    def __init__(self, partner1, partner2, rel_duration):
        _id = 0
        self.p1_cell_no = partner1.cell_no
        self.p2_cell_no = partner2.cell_no
        self.rel_duration = rel_duration
		
    def _create(self):
        _rel = {'p_cell_no':[self.p1_cell_no, self.p2_cell_no],
				'rel_duration': self.rel_duration
				}
				
        return _rel
 
	       
@app.route('/',methods =['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
		
    elif request.method == 'POST':
    
	    #- Acqure Details from Form
        p1Gender = request.form['p1Gender']
        p1Name = request.form['p1Name']
        p1Surname = request.form['p1Surname']
        p1DOB = request.form['p1DOB']
        p1Cell = request.form['p1Cell']
        p1Email = request.form['p1Email']
        p1Occupation = request.form['p1Occupation']
        p1PlaceOfBirth = request.form['p1PlaceOfBirth']	
        p1CurrentPlace = request.form['p1CurrentPlace']
    
        p2Gender = request.form['p2Gender']
        p2Name = request.form['p2Name']
        p2Surname = request.form['p2Surname']
        p2DOB = request.form['p2DOB']
        p2Cell = request.form['p2Cell']
        p2PlaceOfBirth = request.form['p2PlaceOfBirth']	
        p2Email = request.form['p2Email']
        p2Occupation = request.form['p2Occupation']
        p2CurrentPlace = request.form['p2CurrentPlace']	
		
		#- Create Details Objects
        partner1 = Person(p1Gender,p1Name, p1Surname, p1DOB, p1Cell, p1Email,p1Occupation,p1PlaceOfBirth, p1CurrentPlace)
        partner2 = Person(p2Gender,p2Name, p2Surname, p2DOB, p2Cell, p2Email,p2Occupation,p2PlaceOfBirth, p2CurrentPlace)
        rel_duration = request.form['relTime1'] + " " + request.form['relTime2']

        #Check for Details
        person1Exits = mongo.db.Person.find({'cell_no':p1Cell})
        person2Exits = mongo.db.Person.find({'cell_no':p2Cell})
		
		#Both Exist
        if person1Exits.count() >= 1 and person2Exits.count() >= 1:
            relationExists = mongo.db.Relation.find({'p_cell_no':[p1Cell,p2Cell]})
            relationExists2 = mongo.db.Relation.find({'p_cell_no':[p2Cell,p1Cell]})
			
            if relationExists.count() >= 1 or relationExists2.count() >= 1 :
                return render_template('result.html')	
            else: #Exits but new relation
                _rel = Relation(partner1,partner2,rel_duration)._create()
				#Wait for Confirm then add
                mongo.db.Relation.insert(_rel)
				
				#After Confirm
                for p in person1Exits:
                    partner1.relations = p['relations']
                partner1.relations.append(str(_rel['_id']))
				
                for p2 in person2Exits:
                    partner2.relations = p2['relations']
                partner2.relations.append(str(_rel['_id']))

				
                mongo.db.Person.update( {'relations':partner1.relations[0],'cell_no':partner1.cell_no},{'$set':{'relations': partner1._json()['relations']}} )
                mongo.db.Person.update( {'relations':partner2.relations[0],'cell_no':partner2.cell_no},{'$set':{'relations': partner2._json()['relations']}} )
                return str(partner1._json()) + " <br/><br/>" + str(partner2._json())
		
		#Only 1 Exist		
        elif person1Exits.count() >= 1 and person2Exits.count() != 1:
            for p in person1Exits:
                person = Person(p['name'], p['surname'], p['date_of_birth'], p['cell_no'], p['Email'],p['occupation'],p['place_of_birth'], p['current_place'])
                person.relations = p['relations']
			
            _rel = Relation(person,partner2,rel_duration)._create()
			
			#Cornfirm
            mongo.db.Relation.insert(_rel)
            person.relations.append(str(_rel['_id']))
            partner2.relations.append(str(_rel['_id']))

            mongo.db.Person.insert(partner2._json())
            mongo.db.Person.update( {'relations':person._json()['relations'][0],'cell_no':person.cell_no},{'$set':{'relations': person._json()['relations']}} )
            return 'Only p1 Exits! added p2 and created a new Relation'
		
		#Only 2 Exist
        elif person1Exits.count() != 1 and person2Exits.count() >= 1:
            for p2 in person2Exits:
                person = Person(p2['name'], p2['surname'], p2['date_of_birth'], p2['cell_no'], p2['Email'],p2['occupation'],p2['place_of_birth'], p2['current_place'])
                person.relations = p2['relations']
			
            _rel = Relation(person,partner2,rel_duration)._create()
            mongo.db.Relation.insert(_rel)
            person.relations.append(str(_rel['_id']))
            partner1.relations.append(str(_rel['_id']))

            mongo.db.Person.insert(partner1._json())
            mongo.db.Person.update( {'relations':person._json()['relations'][0],'name':partner2.name},{'$set':{'relations': person._json()['relations']}} )
            return 'Only p2 Exist! should added p1 and created a new Relation'
		#Both dont Exist
        else:
            _relation = Relation(partner1,partner2,rel_duration)._create()
            mongo.db.Relation.insert(_relation)
            partner1.relations.append(str(_relation['_id']))
            partner2.relations.append(str(_relation['_id']))
            
            mongo.db.Person.insert(partner1._json())
            mongo.db.Person.insert(partner2._json())
            return 'They both dont Exist! but added with relation'
            			
            
        return 'hola'
		
	
	
if __name__ == '__main__':
    app.run(debug = True)
	
	