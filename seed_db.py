
from routes import db, Manufacturer, Type, Model, Part, User


def seeder():

    def manufacturer_seed(manu_name):
        # return Manufacturer(manufacturer_name = manu_name)
        return Manufacturer(name=manu_name)

    def type_seed(type_name):
        return Type(name=type_name)

    def model_seed(mod_name):
        return Model(name=mod_name)

    def part_seed(name, manufacturer_id, type_id, model_id):

        return Part(name=name, manufID=manufacturer_id, typeID=type_id, modelID=model_id)

    def user_seed(uname, uemail, active):
        return User(name=uname, email=uemail, is_active=active)

    # Hardcoded Data
    manList = ['Benz', 'BMW', 'Audi', 'Tesla', 'Ford', 'Toyota']
    typeList = ['Sedan', 'Coupe', 'SUV', 'Hybrid']
    modelList = ['S 300', 'Tesla X', 'E-tron', 'i7', 'Land Crouser', 'Mostang']
    partList = [['Headlights', 1, 1, 1],
                ['Battery', 4, 1, 2],
                ['Steering wheel', 3, 2, 4],
                ['Speedometer', 6, 3, 5],
                ['GearShift', 5, 3, 6]]
    userList = [['Hamed', 'ihamedbco@gmail.com', 1]]

    # Insert Data To Tabels
    try:

        for ctr in manList:
            db.session.add(manufacturer_seed(ctr))
        db.session.commit()

        for ctr in typeList:
            db.session.add(type_seed(ctr))
        db.session.commit()

        for ctr in modelList:
            db.session.add(model_seed(ctr))
        db.session.commit()

        for ind, ctr in enumerate(partList):
            db.session.add(part_seed(ctr[0], ctr[1], ctr[2], ctr[3]))
        db.session.commit()

        for ctr in userList:
            db.session.add(user_seed(ctr[0], ctr[1], ctr[2]))
        db.session.commit()

        db.session.commit()
        return 'Successful Database Seed!'

    except Exception as e:
        db.session.rollback()
        print(e)
