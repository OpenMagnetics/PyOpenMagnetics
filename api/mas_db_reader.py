import sqlalchemy
import pandas
from sqlalchemy import Integer, Float
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.dialects import postgresql
import os
import MAS
import PyOpenMagnetics


class Database:
    def connect(self, schema='public'):
        raise NotImplementedError

    def disconnect(self):
        self.session.close()


class IntermediateMasTable(Database):

    def __init__(self, debug=False):
        self.debug = debug

    def print_query(self, query):
        print(query.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))

    def expand_material(self, magnetic):
        material_name = magnetic.core.functionalDescription.material
        material_data = PyOpenMagnetics.get_material_data(material_name)
        magnetic.core.functionalDescription.material = MAS.CoreMaterial.from_dict(material_data)
        return magnetic

    def connect(self, schema='public'):
        driver = "postgresql"
        address = os.getenv('OM_DB_ADDRESS')
        port = os.getenv('OM_DB_PORT')
        name = os.getenv('OM_DB_NAME')
        user = os.getenv('OM_DB_USER')
        password = os.getenv('OM_DB_PASSWORD')

        self.engine = sqlalchemy.create_engine(f"{driver}://{user}:{password}@{address}:{port}/{name}")

        metadata = sqlalchemy.MetaData()
        metadata.reflect(self.engine, schema=schema)
        Base = automap_base(metadata=metadata)
        Base.prepare()

        Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = Session()
        self.Table = Base.classes.intermediate_mas

    def get_mas(self, limit=1):
        self.connect()
        query = self.session.query(self.Table).limit(limit)
        data = pandas.read_sql(query.statement, query.session.bind)
        data["mas"] = data.apply(lambda row: MAS.Mas.from_dict(row["mas"]), axis=1)
        self.disconnect()
        return data

    def get_magnetic(self, limit=1):
        self.connect()
        query = self.session.query(self.Table.mas["magnetic"].label("magnetic")).limit(limit)
        data = pandas.read_sql(query.statement, query.session.bind)
        data["magnetic"] = data.apply(lambda row: MAS.Magnetic.from_dict(row["magnetic"]), axis=1)
        self.disconnect()
        return data

    def get_magnetic_by_core_shape(self, shape, limit=1):
        self.connect()
        query = self.session.query(self.Table.mas["magnetic"].label("magnetic")).filter(self.Table.mas["magnetic"]["core"]["functionalDescription"]["shape"]["name"].astext == shape).limit(limit)
        data = pandas.read_sql(query.statement, query.session.bind)
        data["magnetic"] = data.apply(lambda row: MAS.Magnetic.from_dict(row["magnetic"]), axis=1)
        self.disconnect()
        return data

    def get_magnetic_by_core_material(self, material, limit=1):
        self.connect()
        query = self.session.query(self.Table.mas["magnetic"].label("magnetic")).filter(self.Table.mas["magnetic"]["core"]["functionalDescription"]["material"].astext == material).limit(limit)
        data = pandas.read_sql(query.statement, query.session.bind)
        data["magnetic"] = data.apply(lambda row: MAS.Magnetic.from_dict(row["magnetic"]), axis=1)
        data["magnetic"] = data.apply(lambda row: self.expand_material(row["magnetic"]), axis=1)
        self.disconnect()
        return data

    def get_magnetic_by_primary_number_turns(self, number_turns, limit=1):
        self.connect()
        query = self.session.query(self.Table.mas["magnetic"].label("magnetic")).filter(self.Table.mas["magnetic"]["coil"]["functionalDescription"][0]["numberTurns"].astext.cast(Integer) == number_turns).limit(limit)

        if self.debug:
            self.print_query(query)
            
        data = pandas.read_sql(query.statement, query.session.bind)
        data["magnetic"] = data.apply(lambda row: MAS.Magnetic.from_dict(row["magnetic"]), axis=1)
        self.disconnect()
        return data

    def get_mas_by_maximum_core_losses(self, core_losses, limit=1):
        self.connect()
        query = self.session.query(self.Table.mas).filter(self.Table.mas["outputs"][0]["coreLosses"]["coreLosses"].astext.cast(Float) < core_losses).limit(limit)
        data = pandas.read_sql(query.statement, query.session.bind)
        data["mas"] = data.apply(lambda row: MAS.Mas.from_dict(row["mas"]), axis=1)
        self.disconnect()
        return data

    def get_mas_by_primary_current_waveform_label(self, label, limit=1):
        self.connect()
        query = self.session.query(self.Table.mas).filter(self.Table.mas["inputs"]["operatingPoints"][0]["excitationsPerWinding"][0]["current"]["processed"]["label"].astext == label).limit(limit)
        data = pandas.read_sql(query.statement, query.session.bind)
        data["mas"] = data.apply(lambda row: MAS.Mas.from_dict(row["mas"]), axis=1)
        self.disconnect()
        return data


if __name__ == '__main__':  # pragma: no cover
    table = IntermediateMasTable()
    data = table.get_magnetic_by_core_shape("PQ 40/40")
    print(data["magnetic"].iloc[0].core.functionalDescription.shape.name)
    print(data["magnetic"].iloc[0].core.functionalDescription.shape.to_dict())
    data = table.get_magnetic_by_core_material("3C91")
    print(data["magnetic"].iloc[0].core.functionalDescription.material.name)
    data = table.get_magnetic_by_primary_number_turns(42)
    print(data["magnetic"].iloc[0].coil.functionalDescription[0])
    data = table.get_mas_by_maximum_core_losses(2)
    print(data["mas"].iloc[0].outputs[0].coreLosses)
    data = table.get_mas_by_primary_current_waveform_label("Triangular")
    print(data["mas"].iloc[0].inputs.operatingPoints[0].excitationsPerWinding[0].current.processed)
